import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from model.roles.registry import ROLE_TO_GROUP_TYPE
from model.types.GroupTypeDefinition import CollectionDefinition


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RootConfig:
    """
    A MiData group that is imported including all its subgroups.

    Attributes:
        id: MiData group ID of the root.
        only_subtrees: If set, only these groups (with all their subgroups) are imported.
            Their parents up to the root are imported as well, all other groups are skipped.
    """
    id: int
    only_subtrees: frozenset[int] = field(default_factory=frozenset)


@dataclass(frozen=True)
class GroupOverride:
    """
    Settings for one specific MiData group, on top of its GroupTypeDefinition.

    Attributes:
        role_subgroups: If False, no role subgroups are created (the "Rollen" container still exists).
        roles_add: Roles that get a subgroup in addition to the type's default_roles.
        roles_remove: Roles of the type's default_roles that get no subgroup.
        collections: If False, no collection groups are created (neither from the type nor extra_collections).
        extra_collections: Collections in addition to the type's collections. Same key overrides the type's one.
    """
    role_subgroups: bool = True
    roles_add: frozenset[str] = field(default_factory=frozenset)
    roles_remove: frozenset[str] = field(default_factory=frozenset)
    collections: bool = True
    extra_collections: tuple[CollectionDefinition, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EventToSync:
    group_id: int
    event_id: int
    short_name: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class ImportConfig:
    keycloak_group_root: str
    fetch_workers: int
    roots: tuple[RootConfig, ...]
    groups: dict[int, GroupOverride]
    events: tuple[EventToSync, ...]

    def group(self, group_id: int | None) -> GroupOverride:
        return self.groups.get(group_id, DEFAULT_GROUP_OVERRIDE) if group_id is not None else DEFAULT_GROUP_OVERRIDE


DEFAULT_GROUP_OVERRIDE = GroupOverride()


def _check_keys(where: str, data: dict[str, Any], allowed: set[str], required: set[str] = frozenset()) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)} (allowed: {sorted(allowed)})")
    missing = set(required) - set(data)
    if missing:
        raise ConfigError(f"{where}: missing keys {sorted(missing)}")


def _expect(where: str, value: Any, expected_type: type | tuple[type, ...]) -> Any:
    # bool is a subclass of int, but must not pass as an ID
    if isinstance(value, bool) and expected_type is not bool:
        raise ConfigError(f"{where}: expected {expected_type}, got {value!r}")
    if not isinstance(value, expected_type):
        raise ConfigError(f"{where}: expected {expected_type}, got {value!r}")
    return value


def _parse_group_id(where: str, key: str) -> int:
    try:
        return int(key)
    except ValueError:
        raise ConfigError(f"{where}: '{key}' is not a MiData group ID") from None


def _parse_int_list(where: str, value: Any) -> frozenset[int]:
    _expect(where, value, list)
    return frozenset(_expect(f"{where}[{i}]", v, int) for i, v in enumerate(value))


def _parse_roles(where: str, value: Any) -> frozenset[str]:
    _expect(where, value, list)
    roles = frozenset(_expect(f"{where}[{i}]", v, str) for i, v in enumerate(value))
    unknown = roles - set(ROLE_TO_GROUP_TYPE)
    if unknown:
        raise ConfigError(f"{where}: unknown roles {sorted(unknown)}")
    return roles


def _parse_collection(where: str, data: Any) -> CollectionDefinition:
    _expect(where, data, dict)
    _check_keys(where, data, {"key", "label", "roles"}, required={"key", "label", "roles"})
    return CollectionDefinition(
        key=_expect(f"{where}.key", data["key"], str),
        label=_expect(f"{where}.label", data["label"], str),
        roles=_parse_roles(f"{where}.roles", data["roles"]),
    )


def _parse_root(where: str, data: Any) -> RootConfig:
    _expect(where, data, dict)
    _check_keys(where, data, {"id", "note", "only_subtrees"}, required={"id"})
    return RootConfig(
        id=_expect(f"{where}.id", data["id"], int),
        only_subtrees=_parse_int_list(f"{where}.only_subtrees", data.get("only_subtrees", [])),
    )


def _parse_group(where: str, data: Any) -> GroupOverride:
    _expect(where, data, dict)
    _check_keys(
        where,
        data,
        {"note", "role_subgroups", "roles_add", "roles_remove", "collections", "extra_collections"},
    )
    extra_collections = _expect(f"{where}.extra_collections", data.get("extra_collections", []), list)
    return GroupOverride(
        role_subgroups=_expect(f"{where}.role_subgroups", data.get("role_subgroups", True), bool),
        roles_add=_parse_roles(f"{where}.roles_add", data.get("roles_add", [])),
        roles_remove=_parse_roles(f"{where}.roles_remove", data.get("roles_remove", [])),
        collections=_expect(f"{where}.collections", data.get("collections", True), bool),
        extra_collections=tuple(
            _parse_collection(f"{where}.extra_collections[{i}]", c) for i, c in enumerate(extra_collections)
        ),
    )


def _parse_events(where: str, data: Any) -> list[EventToSync]:
    # [events.<group_id>] contains lists with any name (e.g. per year), only used for grouping
    _expect(where, data, dict)
    events: list[EventToSync] = []
    for group_key, lists in data.items():
        group_where = f"{where}.{group_key}"
        group_id = _parse_group_id(group_where, group_key)
        _expect(group_where, lists, dict)
        for label, items in lists.items():
            list_where = f"{group_where}.{label}"
            _expect(list_where, items, list)
            for i, item in enumerate(items):
                item_where = f"{list_where}[{i}]"
                _expect(item_where, item, dict)
                _check_keys(item_where, item, {"id", "short_name", "comment"}, required={"id"})
                events.append(EventToSync(
                    group_id=group_id,
                    event_id=_expect(f"{item_where}.id", item["id"], int),
                    short_name=_expect(f"{item_where}.short_name", item.get("short_name", ""), str) or None,
                    comment=_expect(f"{item_where}.comment", item.get("comment", ""), str) or None,
                ))
    return events


def parse_config(data: dict[str, Any]) -> ImportConfig:
    _check_keys("config", data, {"keycloak_group_root", "fetch_workers", "roots", "groups", "events"}, required={"roots"})

    roots_data = _expect("roots", data["roots"], list)
    roots = tuple(_parse_root(f"roots[{i}]", r) for i, r in enumerate(roots_data))
    if not roots:
        raise ConfigError("roots: at least one root group is required")
    root_ids = [r.id for r in roots]
    if len(root_ids) != len(set(root_ids)):
        raise ConfigError(f"roots: duplicate root IDs in {root_ids}")

    groups_data = _expect("groups", data.get("groups", {}), dict)
    groups = {
        _parse_group_id("groups", key): _parse_group(f"groups.{key}", value)
        for key, value in groups_data.items()
    }

    events = _parse_events("events", data.get("events", {}))
    seen_event_ids: set[int] = set()
    for event in events:
        if event.event_id in seen_event_ids:
            raise ConfigError(f"events: event ID {event.event_id} is listed more than once")
        seen_event_ids.add(event.event_id)

    fetch_workers = _expect("fetch_workers", data.get("fetch_workers", 10), int)
    if fetch_workers < 1:
        raise ConfigError("fetch_workers: must be at least 1")

    return ImportConfig(
        keycloak_group_root=_expect("keycloak_group_root", data.get("keycloak_group_root", "midata"), str),
        fetch_workers=fetch_workers,
        roots=roots,
        groups=groups,
        events=tuple(events),
    )


def load_config(path: str | Path) -> ImportConfig:
    path = Path(path)
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path}: invalid TOML: {e}") from None

    try:
        return parse_config(data)
    except ConfigError as e:
        raise ConfigError(f"{path}: {e}") from None
