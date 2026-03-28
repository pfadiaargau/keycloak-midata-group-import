import importlib
import inspect
import pkgutil
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class RoleLocation:
    module: str
    class_name: str
    member_name: str
    role_value: str
    group_type: str


ROLE_ENUM_CLASSES: list[type[Enum]] = []
GROUP_TYPE_ROLES: dict[str, frozenset[str]] = {}
ROLE_TO_GROUP_TYPE: dict[str, str] = {}
ROLE_LOCATIONS: dict[str, RoleLocation] = {}


def _extract_string_meta(value, label: str, enum_cls: type[Enum]) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, Enum) and isinstance(value.value, str):
        return value.value

    if hasattr(value, "value") and isinstance(value.value, str):
        return value.value

    raise ValueError(
        f"{enum_cls.__module__}.{enum_cls.__name__}: "
        f"{label} muss ein String sein, ist aber {value!r}"
    )


def _get_group_type(enum_cls: type[Enum]) -> str:
    if not hasattr(enum_cls, "GROUP_TYPE"):
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: GROUP_TYPE fehlt"
        )

    raw_group_type = getattr(enum_cls, "GROUP_TYPE")
    group_type = _extract_string_meta(raw_group_type, "GROUP_TYPE", enum_cls)

    if not group_type.strip():
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: GROUP_TYPE darf nicht leer sein"
        )

    return group_type


def _get_group_prefix(enum_cls: type[Enum], group_type: str) -> str:
    if not hasattr(enum_cls, "GROUP_PREFIX"):
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: GROUP_PREFIX fehlt"
        )

    raw_group_prefix = getattr(enum_cls, "GROUP_PREFIX")
    group_prefix = _extract_string_meta(raw_group_prefix, "GROUP_PREFIX", enum_cls)

    expected_prefix = group_type + "::"

    if group_prefix != expected_prefix:
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: "
            f"GROUP_PREFIX ist {group_prefix!r}, erwartet wäre {expected_prefix!r}"
        )

    return group_prefix


def load_role_definitions(package_name: str = "model.roles") -> None:
    global ROLE_ENUM_CLASSES, GROUP_TYPE_ROLES, ROLE_TO_GROUP_TYPE, ROLE_LOCATIONS

    try:
        package = importlib.import_module(package_name)
    except Exception as e:
        raise RuntimeError(
            f"Das Paket {package_name!r} konnte nicht importiert werden:\n{e}"
        ) from e

    role_enum_classes: list[type[Enum]] = []
    group_type_roles: dict[str, set[str]] = defaultdict(set)
    role_to_group_type: dict[str, str] = {}
    role_locations: dict[str, RoleLocation] = {}

    for module_info in pkgutil.walk_packages(package.__path__, package_name + "."):
        module_name = module_info.name

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            raise RuntimeError(
                f"Fehler beim Import von Modul {module_name!r}:\n{e}"
            ) from e

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is Enum:
                continue
            if not issubclass(obj, Enum):
                continue
            if obj.__module__ != module.__name__:
                continue

            group_type = _get_group_type(obj)
            group_prefix = _get_group_prefix(obj, group_type)

            members = list(obj)
            if not members:
                continue

            role_enum_classes.append(obj)

            for member in members:
                member_name = member.name
                role_value = member.value

                # Meta-Members überspringen
                if member_name in {"GROUP_TYPE", "GROUP_PREFIX"}:
                    continue

                if not isinstance(role_value, str):
                    raise ValueError(
                        f"Ungültiger Rollenwert in {obj.__module__}.{obj.__name__}.{member_name}: "
                        f"{role_value!r} ist kein String"
                    )

                if not role_value.startswith(group_prefix):
                    raise ValueError(
                        f"Ungültiger Rollenwert in {obj.__module__}.{obj.__name__}.{member_name}: "
                        f"{role_value!r} beginnt nicht mit {group_prefix!r}"
                    )

                existing = role_locations.get(role_value)
                if existing:
                    raise ValueError(
                        "Doppelter Rollenwert erkannt.\n\n"
                        f"Rollenwert: {role_value}\n\n"
                        "Erste Definition:\n"
                        f"  Modul:  {existing.module}\n"
                        f"  Klasse: {existing.class_name}\n"
                        f"  Member: {existing.member_name}\n"
                        f"  Typ:    {existing.group_type}\n\n"
                        "Zweite Definition:\n"
                        f"  Modul:  {obj.__module__}\n"
                        f"  Klasse: {obj.__name__}\n"
                        f"  Member: {member_name}\n"
                        f"  Typ:    {group_type}\n"
                    )

                role_locations[role_value] = RoleLocation(
                    module=obj.__module__,
                    class_name=obj.__name__,
                    member_name=member_name,
                    role_value=role_value,
                    group_type=group_type,
                )

                role_to_group_type[role_value] = group_type
                group_type_roles[group_type].add(role_value)

    ROLE_ENUM_CLASSES = sorted(
        role_enum_classes,
        key=lambda c: (c.__module__, c.__name__),
    )
    GROUP_TYPE_ROLES = {
        group_type: frozenset(sorted(values))
        for group_type, values in sorted(group_type_roles.items(), key=lambda x: x[0])
    }
    ROLE_TO_GROUP_TYPE = dict(sorted(role_to_group_type.items(), key=lambda x: x[0]))
    ROLE_LOCATIONS = dict(sorted(role_locations.items(), key=lambda x: x[0]))


def print_role_registry_summary() -> None:
    print("Role Registry Summary")
    print("====================")
    print(f"Gefundene Rollenklassen: {len(ROLE_ENUM_CLASSES)}")
    print(f"Gefundene Gruppentypen:  {len(GROUP_TYPE_ROLES)}")
    print(f"Gefundene Rollen:        {len(ROLE_TO_GROUP_TYPE)}")
    print()

    for group_type, roles in GROUP_TYPE_ROLES.items():
        print(f"{group_type} ({len(roles)} Rollen)")
        for role in roles:
            loc = ROLE_LOCATIONS.get(role)
            if loc:
                print(f"  - {role} [{loc.class_name}.{loc.member_name}]")
            else:
                print(f"  - {role}")
        print()


load_role_definitions()