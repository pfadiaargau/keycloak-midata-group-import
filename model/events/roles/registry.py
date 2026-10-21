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
    event_type: str


ROLE_ENUM_CLASSES: list[type[Enum]] = []
EVENT_TYPE_ROLES: dict[str, frozenset[str]] = {}
ROLE_TO_EVENT_TYPE: dict[str, str] = {}
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
        f"{label} must be a string, but is {value!r}"
    )


def _get_event_type(enum_cls: type[Enum]) -> str:
    if not hasattr(enum_cls, "EVENT_TYPE"):
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: EVENT_TYPE is missing"
        )

    raw_event_type = getattr(enum_cls, "EVENT_TYPE")
    event_type = _extract_string_meta(raw_event_type, "EVENT_TYPE", enum_cls)

    if not event_type.strip():
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: EVENT_TYPE must not be empty"
        )

    return event_type


def _get_event_prefix(enum_cls: type[Enum], event_type: str) -> str:
    if not hasattr(enum_cls, "EVENT_PREFIX"):
        raise ValueError(
            f"{enum_cls.__module__}.{enum_cls.__name__}: EVENT_PREFIX is missing"
        )

    raw_event_prefix = getattr(enum_cls, "EVENT_PREFIX")
    event_prefix = _extract_string_meta(raw_event_prefix, "EVENT_PREFIX", enum_cls)

    return event_prefix


def load_role_definitions(package_name: str = "model.events.roles") -> None:
    global ROLE_ENUM_CLASSES, EVENT_TYPE_ROLES, ROLE_TO_EVENT_TYPE, ROLE_LOCATIONS

    try:
        package = importlib.import_module(package_name)
    except Exception as e:
        raise RuntimeError(
            f"Could not import package {package_name!r}:\n{e}"
        ) from e

    role_enum_classes: list[type[Enum]] = []
    event_type_roles: dict[str, set[str]] = defaultdict(set)
    role_to_event_type: dict[str, str] = {}
    role_locations: dict[str, RoleLocation] = {}

    for module_info in pkgutil.walk_packages(package.__path__, package_name + "."):
        module_name = module_info.name

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            raise RuntimeError(
                f"Error importing module {module_name!r}:\n{e}"
            ) from e

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is Enum:
                continue
            if not issubclass(obj, Enum):
                continue
            if obj.__module__ != module.__name__:
                continue

            event_type = _get_event_type(obj)
            event_prefix = _get_event_prefix(obj, event_type)

            members = list(obj)
            if not members:
                continue

            role_enum_classes.append(obj)

            for member in members:
                member_name = member.name
                role_value = member.value

                # Skip meta members
                if member_name in {"EVENT_TYPE", "EVENT_PREFIX"}:
                    continue

                if not isinstance(role_value, str):
                    raise ValueError(
                        f"Invalid role value in {obj.__module__}.{obj.__name__}.{member_name}: "
                        f"{role_value!r} is not a string"
                    )

                role_locations[role_value] = RoleLocation(
                    module=obj.__module__,
                    class_name=obj.__name__,
                    member_name=member_name,
                    role_value=role_value,
                    event_type=event_type,
                )

                role_to_event_type[role_value] = event_type
                event_type_roles[event_type].add(role_value)

    ROLE_ENUM_CLASSES = sorted(
        role_enum_classes,
        key=lambda c: (c.__module__, c.__name__),
    )
    EVENT_TYPE_ROLES = {
        event_type: frozenset(sorted(values))
        for event_type, values in sorted(event_type_roles.items(), key=lambda x: x[0])
    }
    ROLE_TO_EVENT_TYPE = dict(sorted(role_to_event_type.items(), key=lambda x: x[0]))
    ROLE_LOCATIONS = dict(sorted(role_locations.items(), key=lambda x: x[0]))


def print_role_registry_summary() -> None:
    print("Role Registry Summary")
    print("====================")
    print(f"Role classes found: {len(ROLE_ENUM_CLASSES)}")
    print(f"Event types found:  {len(EVENT_TYPE_ROLES)}")
    print(f"Roles found:        {len(ROLE_TO_EVENT_TYPE)}")
    print()

    for event_type, roles in EVENT_TYPE_ROLES.items():
        print(f"{event_type} ({len(roles)} roles)")
        for role in roles:
            loc = ROLE_LOCATIONS.get(role)
            if loc:
                print(f"  - {role} [{loc.class_name}.{loc.member_name}]")
            else:
                print(f"  - {role}")
        print()


load_role_definitions()