import json
import os
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests
from dotenv import load_dotenv
from model.EventDefinitions import EVENT_DEFINITIONS
from model.GroupDefinitions import GROUP_DEFINITIONS
from model.groups.MidataGroups import MidataGroups
from model.roles.abteilung import AbteilungRoles
from model.types.EventTypeDefinition import EventTypeDefinition
from model.types.GroupTypeDefinition import (CollectionDefinition,
                                             GroupTypeDefinition)
from services.KeycloakApiService import KeycloakApiService
from services.MidataApiService import MidataAPIService

load_dotenv()

RECREATE_HIRARCHY = True

RAW_ROOTS_JSON_FILE = "detailed_hierarchy.json"
CATEGORIZED_ROOTS_JSON_FILE = "categorized_groups.json"

# Anzahl paralleler Requests an MIDATA (Gruppennamen, Events)
MIDATA_FETCH_WORKERS = 10

KEYCLOAK_GROUP_ROOT = os.getenv("KEYCLOAK_GROUP_ROOT", "midata")

# Mehrere Startknoten statt nur ein Root
MIDATA_ROOT_GROUP_IDS = [
    int(x.strip())
    for x in os.getenv("MIDATA_ROOT_GROUP_IDS").split(",")
    if x.strip()
]

# Rollen-Container wird immer erzeugt
ROLE_SUBGROUP_NAME = "Rollen"

# Container für Sammelgruppen, wird nur erzeugt wenn die Gruppe Sammlungen hat
COLLECTION_SUBGROUP_NAME = "Sammlungen"

# Optional: Events
# - group_id: ID der MIDATA-Gruppe
# - event_id: ID des Events
# - short_name: optionaler kurzer Name des Events
# - comment: optionale Beschreibung, wird als Attribut "comment" in Keycloak gespeichert
EVENTS_TO_SYNC = [
    # {"group_id": 400, "event_id": 2778, "short_name": "AG333-26"}
    
    # 2027
    # Zeltbasiskurs Pfadistufe (AG 121-27)
    {"group_id": 4691, "event_id": 35221, "comment": "Zeltbasiskurs Pfadistufe (AG 121-27)"},
    # Aufbau gemischt 2 (SO 252-27)
    {"group_id": 4691, "event_id": 35081, "comment": "Aufbau gemischt 2 (SO 252-27)"},
    # Aufbau gemischt 3 (SO 253-27)
    {"group_id": 4691, "event_id": 35083, "comment": "Aufbau gemischt 3 (SO 253-27)"},
    # Basiskurs gemischt 1 (AG 151-27)
    {"group_id": 4691, "event_id": 35222, "comment": "Basiskurs gemischt 1 (AG 151-27)"},
    # Aufbau gemischt 1 (SO 251-27)
    {"group_id": 4691, "event_id": 35082, "comment": "Aufbau gemischt 1 (SO 251-27)"},
    # Basiskurs gemischt 2 (AG 152-27)
    {"group_id": 4691, "event_id": 35223, "comment": "Basiskurs gemischt 2 (AG 152-27)"},
    # Basiskurs Wolfstufe (AG 111-27)
    {"group_id": 4691, "event_id": 34849, "comment": "Basiskurs Wolfstufe (AG 111-27)"},
    
    # 2026
    # Aufbaukurs Wolfstufe (AG 211-26)
    {"group_id": 4691, "event_id": 31600, "comment": "Aufbaukurs Wolfstufe (AG 211-26)"},
    # Aufbaukurs Pfadistufe (AG 221-26)
    {"group_id": 4691, "event_id": 31598, "comment": "Aufbaukurs Pfadistufe (AG 221-26)"},
    # Aufbaukurs gemischt (AG 251-26)
    {"group_id": 4691, "event_id": 31599, "comment": "Aufbaukurs gemischt (AG 251-26)"},
    # Sicherheitsmodul Berg 2026 (AG 563-26)
    {"group_id": 4691, "event_id": 32108, "comment": "Sicherheitsmodul Berg 2026 (PBS CH AG 563-26)"},
    # Basiskurs gemischt (SO 122-26)
    {"group_id": 4691, "event_id": 31603, "comment": "Basiskurs gemischt (SO 122-26)"},

    # 2025
    # Futura 4 Herbst (AG 051-25)
    {"group_id": 4691, "event_id": 29699, "comment": "Futura 4 Herbst (AG 051-25)"},
    # Basiskurs Wolfsstufe 1 (AG 111-25)
    {"group_id": 4691, "event_id": 27837, "comment": "Basiskurs Wolfsstufe 1 (AG 111-25)"},
    # Zeltbasiskurs Pfadistufe (AG 121-25)
    {"group_id": 4691, "event_id": 27830, "comment": "Zeltbasiskurs Pfadistufe (AG 121-25)"},
    # Hausbasiskurs Pfadistufe (AG 122-25)
    {"group_id": 4691, "event_id": 28224, "comment": "Hausbasiskurs Pfadistufe (AG 122-25)"},
    # Aufbaukurs Pfadistufe (SO 221-25)
    {"group_id": 4691, "event_id": 27831, "comment": "Aufbaukurs Pfadistufe (SO 221-25)"},
    # Aufbaukurs gemischt (SO 252-25)
    {"group_id": 4691, "event_id": 27832, "comment": "Aufbaukurs gemischt (SO 252-25)"},
    # MF Inklusion (SO 555-25)
    {"group_id": 4691, "event_id": 29069, "comment": "MF Inklusion (PBS CH SO 555-25)"},

    # 2024
    # Aufbaukurs Pfadistufe (AG 221-24)
    {"group_id": 4691, "event_id": 24120, "comment": "Aufbaukurs Pfadistufe (AG 221-24)"},
    # Wochenendaufbaukurs Pfadistufe (AG 222-24)
    {"group_id": 4691, "event_id": 24121, "comment": "Wochenendaufbaukurs Pfadistufe (AG 222-24)"},
    # Futura 1 (SO 051-24)
    {"group_id": 4691, "event_id": 24161, "comment": "Futura 1 (SO 051-24)"},
    # Basiskurs Wolfsstufe 1 (SO 111-24)
    {"group_id": 4691, "event_id": 24114, "comment": "Basiskurs Wolfsstufe 1 (SO 111-24)"},
    # Basiskurs Wolfsstufe 2 (SO 112-24)
    {"group_id": 4691, "event_id": 24115, "comment": "Basiskurs Wolfsstufe 2 (SO 112-24)"},
    # Hausbasiskurs Pfadistufe (SO 122-24)
    {"group_id": 4691, "event_id": 24117, "comment": "Hausbasiskurs Pfadistufe (SO 122-24)"},

    # 2023
    # Basiskurs Wolfsstufe 1 (AG 111-23)
    {"group_id": 4691, "event_id": 20799, "comment": "Basiskurs Wolfsstufe 1 (AG 111-23)"},
    # Zeltbasiskurs Pfadistufe (AG 121-23)
    {"group_id": 4691, "event_id": 20811, "comment": "Zeltbasiskurs Pfadistufe (AG 121-23)"},
    # Basiskurs Pfadistufe (AG 122-23)
    {"group_id": 4691, "event_id": 20812, "comment": "Basiskurs Pfadistufe (AG 122-23)"},
    # Modul Sanität (AG 554-23)
    {"group_id": 4691, "event_id": 21372, "comment": "Modul Sanität (PBS CH AG 554-23) KS"},
    # Aufbaukurs Wolfsstufe (SO 211-23)
    {"group_id": 4691, "event_id": 20797, "comment": "Aufbaukurs Wolfsstufe (SO 211-23)"},
    # Aufbaukurs Pfadistufe (SO 221-23)
    {"group_id": 4691, "event_id": 20798, "comment": "Aufbaukurs Pfadistufe (SO 221-23)"},
    # Aufbaukurs Pfadistufe/Wolfsstufe (SO 251-23)
    {"group_id": 4691, "event_id": 20800, "comment": "Aufbaukurs Pfadistufe/Wolfsstufe (SO 251-23)"},

    # 2022
    # Aufbaukurs Pfadistufe 1 (AG 221-22)
    {"group_id": 4691, "event_id": 18059, "comment": "Aufbaukurs Pfadistufe 1 (AG 221-22)"},
    # Aufbaukurs Pfadistufe/Wolfsstufe (AG 261-22)
    {"group_id": 4691, "event_id": 18061, "comment": "Aufbaukurs Pfadistufe/Wolfsstufe (AG 261-22)"},
    # Modul Sanität (AG 551-22)
    {"group_id": 4691, "event_id": 18222, "comment": "Modul Sanität (PBS CH AG 551-22)"},
    # Basiskurs Wolfsstufe 1 (SO 111-22)
    {"group_id": 4691, "event_id": 18060, "comment": "Basiskurs Wolfsstufe 1 (SO 111-22)"},
    # Basiskurs Wolfsstufe 2 (SO 112-22)
    {"group_id": 4691, "event_id": 18065, "comment": "Basiskurs Wolfsstufe 2 (SO 112-22)"},
    # Zeltbasiskurs Pfadistufe (SO 121-22)
    {"group_id": 4691, "event_id": 18054, "comment": "Zeltbasiskurs Pfadistufe (SO 121-22)"},
    # Wochenendbasis Pfadistufe (SO 122-22)
    {"group_id": 4691, "event_id": 18057, "comment": "Wochenendbasis Pfadistufe (SO 122-22)"},

    # 2021
    # Futura 1 (AG 051-21 C-19)
    {"group_id": 4691, "event_id": 14405, "comment": "Futura 1 (AG 051-21 C-19)"},
    # Basiskurs Wolfsstufe (AG 111-21)
    {"group_id": 4691, "event_id": 14056, "comment": "Basiskurs Wolfsstufe (AG 111-21)"},
    # Zeltbasiskurs Pfadistufe (AG 121-21 C-19)
    {"group_id": 4691, "event_id": 14060, "comment": "Zeltbasiskurs Pfadistufe (AG 121-21 C-19)"},
    # Basiskurs Pfadistufe (AG 122-21)
    {"group_id": 4691, "event_id": 14061, "comment": "Basiskurs Pfadistufe (AG 122-21) (teildigital)"},
    # Modul Wasser inkl. SLRG (AG 551-21)
    {"group_id": 4691, "event_id": 14276, "comment": "Modul Wasser inkl. SLRG (PBS CH AG 551-21)"},
    # Aufbaukurs Wolfsstufe 2 (SO 212-21)
    {"group_id": 4691, "event_id": 14063, "comment": "Aufbaukurs Wolfsstufe 2 (SO 212-21)"},
    # Aufbaukurs Pfadistufe 1 (SO 221-21)
    {"group_id": 4691, "event_id": 14055, "comment": "Aufbaukurs Pfadistufe 1 (SO 221-21)"},
    # Aufbaukurs Pfadistufe 2 (SO 222-21)
    {"group_id": 4691, "event_id": 14058, "comment": "Aufbaukurs Pfadistufe 2 (SO 222-21)"},

    # 2020
    # Sockout 2 (AG 032-20 C-19)
    {"group_id": 4691, "event_id": 10589, "comment": "Sockout 2 (AG 032-20 C-19)"},
    # Aufbaukurs Wolfsstufe 2 (AG 212-20 C-19)
    {"group_id": 4691, "event_id": 10045, "comment": "Aufbaukurs Wolfsstufe 2 (AG 212-20 C-19)"},
    # Aufbaukurs Pfadistufe 1 (AG 221-20 C-19)
    {"group_id": 4691, "event_id": 10042, "comment": "Aufbaukurs Pfadistufe 1 (AG 221-20 C-19)"},
    # Aufbaukurs Piostufe (AG 231-20 C-19)
    {"group_id": 4691, "event_id": 10050, "comment": "Aufbaukurs Piostufe (AG 231-20 C-19)"},
    # Basiskurs Wolfsstufe (SO 111-20 C-19)
    {"group_id": 4691, "event_id": 10039, "comment": "Basiskurs Wolfsstufe (SO 111-20 C-19)"},
    # Herbstbasis Wolfsstufe 2 (SO 113-20)
    {"group_id": 4691, "event_id": 13115, "comment": "Herbstbasis Wolfsstufe 2 (SO 113-20)"},
    # Basiskurs Pfadistufe Zelt (SO 121-20 C-19)
    {"group_id": 4691, "event_id": 10046, "comment": "Basiskurs Pfadistufe Zelt (SO 121-20 C-19)"},
    # Herbstbasis Pfadistufe (SO 124-20)
    {"group_id": 4691, "event_id": 13116, "comment": "Herbstbasis Pfadistufe (SO 124-20)"},

    # 2019
    # Basiskurs Pfadistufe Haus (AG 122-19)
    {"group_id": 4691, "event_id": 7262, "comment": "Basiskurs Pfadistufe Haus (AG 122-19)"},
    # Aufbaukurs Wolfsstufe (SO 211-19)
    {"group_id": 4691, "event_id": 7252, "comment": "Aufbaukurs Wolfsstufe (SO 211-19)"},
    # Aufbaukurs Pfadistufe 2 (SO 222-19)
    {"group_id": 4691, "event_id": 7258, "comment": "Aufbaukurs Pfadistufe 2 (SO 222-19)"},

]

# Zusätzliche Sammelgruppen pro konkreter MIDATA-Gruppe (ergänzend zu GroupTypeDefinition.collections).
# Mitglied wird, wer eine der Rollen in dieser Gruppe oder einer Gruppe darunter hat.
COLLECTION_GROUPS: dict[int, tuple[CollectionDefinition, ...]] = {
    # Beispiel:
    # 400: (
    #     CollectionDefinition(
    #         key="all_leaders",
    #         label="Alle Leitenden",
    #         roles=frozenset({
    #             "Group::Woelfe::Einheitsleitung",
    #             "Group::Pfadi::Einheitsleitung",
    #         }),
    #     ),
    # ),
}

# Override pro konkreter MIDATA-Gruppe
ROLE_GROUP_OVERRIDES: dict[int, dict[str, set[str]]] = {
    # Beispiel:
    # 400: {
    #     "whitelist": {
    #         "Group::Abteilung::Webmaster",
    #         AbteilungRoles.MATERIALWART.value,
    #     },
    #     "blacklist": {
    #         "Group::Abteilung::Sekretariat",
    #     },
    # },
}


def now_s(start_time: float) -> str:
    return f"{time.perf_counter() - start_time:.2f}s"


def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")


def log_warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}")


def parse_env() -> dict[str, str]:
    load_dotenv()

    required_vars = [
        "MIDATA_ROOT_GROUP_IDS",
        "MIDATA_SERVICE_ACCOUNT_TOKEN",
        "MIDATA_URL",
        "KEYCLOAK_URL",
        "KEYCLOAK_REALM",
        "KEYCLOAK_USER_REALM",
        "KEYCLOAK_USERNAME",
        "KEYCLOAK_PASSWORD",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return {
        "midata_token": os.getenv("MIDATA_SERVICE_ACCOUNT_TOKEN", ""),
        "midata_url": os.getenv("MIDATA_URL", ""),
        "keycloak_url": os.getenv("KEYCLOAK_URL", ""),
        "keycloak_realm": os.getenv("KEYCLOAK_REALM", ""),
        "keycloak_user_realm": os.getenv("KEYCLOAK_USER_REALM", ""),
        "keycloak_username": os.getenv("KEYCLOAK_USERNAME", ""),
        "keycloak_password": os.getenv("KEYCLOAK_PASSWORD", ""),
    }


def ensure_keycloak_root(keycloak_service: KeycloakApiService, root_path: str) -> str:
    path_parts = [p for p in root_path.split("/") if p.strip()]

    if not keycloak_service.check_keycloak_group_path(path_parts):
        log_info(f"Keycloak root path '{root_path}' does not exist. Creating it.")
        keycloak_service.create_group_path(path_parts)

    root_id = keycloak_service.get_group_id_by_path(path_parts)
    if not root_id:
        raise RuntimeError(f"Could not resolve Keycloak group id for path: {root_path}")

    return root_id


def fetch_midata_group_list(midata_url: str, midata_token: str) -> list[dict[str, Any]]:
    headers = {
        "X-Token": midata_token,
        "Content-Type": "application/json",
    }

    response = requests.get(f"{midata_url}/list_groups", headers=headers, timeout=60)
    response.raise_for_status()

    payload = response.json()
    groups = payload.get("groups")
    if not isinstance(groups, list):
        raise RuntimeError("MIDATA /list_groups response does not contain a valid 'groups' list.")

    return groups


def build_group_children_index(groups: list[dict[str, Any]]) -> dict[int | None, list[dict[str, Any]]]:
    children_by_parent: dict[int | None, list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        children_by_parent[group.get("parent_id")].append(group)
    return children_by_parent


def fetch_group_name(
    midata_service: MidataAPIService,
    group_id: int,
) -> str | None:

    group_info = midata_service.get_group_info(group_id)

    if not group_info:
        raise RuntimeError(f"Could not fetch group info for group ID {group_id}")

    attributes = group_info.get("attributes", {})

    name = attributes.get("name")

    if not name:
        raise RuntimeError(f"Group ID {group_id} has no name in attributes")

    return name



def collect_subtree_ids(
    root_id: int,
    children_by_parent: dict[int | None, list[dict[str, Any]]],
) -> list[int]:
    ids: list[int] = []
    stack = [root_id]
    while stack:
        group_id = stack.pop()
        ids.append(group_id)
        stack.extend(child["id"] for child in children_by_parent.get(group_id, []))
    return ids


def fetch_group_names(
    midata_service: MidataAPIService,
    group_ids: list[int],
) -> dict[int, str | Exception]:
    """Lädt die Namen parallel. Fehler werden als Exception im Ergebnis abgelegt."""

    def fetch(group_id: int) -> str | Exception:
        try:
            return fetch_group_name(midata_service, group_id)
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=MIDATA_FETCH_WORKERS) as executor:
        return dict(zip(group_ids, executor.map(fetch, group_ids)))


def build_raw_tree(
    root_group: dict[str, Any],
    children_by_parent: dict[int | None, list[dict[str, Any]]],
    group_names: dict[int, str | Exception],
    *,
    is_root: bool = False,
    parent_id: int | None = None,
) -> dict[str, Any] | None:
    node = dict(root_group)

    name = group_names.get(node["id"])
    if name is None:
        name = RuntimeError("Group name was not fetched")

    if isinstance(name, Exception):
        e = name
        msg = (
            f"group_id={node.get('id')}, "
            f"type={node.get('type')}, "
            f"parent_id={parent_id}: {e}"
        )

        if is_root:
            raise RuntimeError(f"Configured root group is invalid: {msg}") from e

        log_warn(f"Skipping node: {msg}")
        return None

    node["name"] = name

    children = children_by_parent.get(node["id"], [])
    node["children"] = [
        child_node
        for child_node in (
            build_raw_tree(
                child,
                children_by_parent,
                group_names,
                is_root=False,
                parent_id=node["id"],
            )
            for child in children
        )
        if child_node is not None
    ]

    return node


def get_group_definition(group_type: str) -> GroupTypeDefinition | None:
    return GROUP_DEFINITIONS.get(group_type)


def get_group_definition_or_fallback(group_type: str) -> GroupTypeDefinition:
    definition = GROUP_DEFINITIONS.get(group_type)
    if definition:
        return definition

    return GroupTypeDefinition(
        type_key=group_type,
        display_name=group_type,
        allowed_roles=frozenset(),
        default_roles=frozenset(),
        children=(),
    )

def get_event_definition(event_type: str | None) -> EventTypeDefinition:
    if event_type and event_type in EVENT_DEFINITIONS:
        return EVENT_DEFINITIONS[event_type]
    return EVENT_DEFINITIONS["default"]

def categorize_group_tree(node: dict[str, Any]) -> dict[str, Any]:
    group_type = node.get("type")
    definition = get_group_definition_or_fallback(group_type)

    raw_children = node.get("children", [])
    categorized_children: dict[str, list[dict[str, Any]]] = {
        child_def.key: []
        for child_def in definition.children
    }

    unknown_children: list[dict[str, Any]] = []

    for child in raw_children:
        child_type = child.get("type")
        matching_category = next(
            (child_def for child_def in definition.children if child_type in child_def.allowed_types),
            None,
        )

        if matching_category:
            categorized_children[matching_category.key].append(categorize_group_tree(child))
        else:
            unknown_children.append(categorize_group_tree(child))

    node_copy = {k: v for k, v in node.items() if k != "children"}

    for key, items in categorized_children.items():
        node_copy[key] = items

    if unknown_children:
        node_copy["unknown_children"] = unknown_children
        log_warn(
            f"Group '{node_copy.get('name')}' ({group_type}) has unknown child types: "
            f"{sorted({c.get('type') for c in unknown_children if c.get('type')})}"
        )

    return node_copy


def validate_collections(owner: str, collections: tuple[CollectionDefinition, ...]) -> None:
    seen_keys: set[str] = set()
    seen_labels: set[str] = set()
    for collection in collections:
        if collection.key in seen_keys:
            raise ValueError(f"{owner}: duplicate collection key '{collection.key}'")
        if collection.label in seen_labels:
            raise ValueError(f"{owner}: duplicate collection label '{collection.label}'")
        if not collection.roles:
            log_warn(f"{owner}: collection '{collection.key}' has no roles and will stay empty")
        seen_keys.add(collection.key)
        seen_labels.add(collection.label)


def validate_group_definitions() -> None:
    all_defined_types = set(GROUP_DEFINITIONS.keys())

    for group_id, collections in COLLECTION_GROUPS.items():
        validate_collections(f"COLLECTION_GROUPS[{group_id}]", collections)

    for group_type, definition in GROUP_DEFINITIONS.items():
        validate_collections(group_type, definition.collections)

        invalid_defaults = definition.default_roles - definition.allowed_roles
        if invalid_defaults:
            raise ValueError(
                f"{group_type}: default_roles are not part of allowed_roles: "
                f"{sorted(invalid_defaults)}"
            )

        seen_keys: set[str] = set()
        for child in definition.children:
            if child.key in seen_keys:
                raise ValueError(f"{group_type}: duplicate child category key '{child.key}'")
            seen_keys.add(child.key)

            unknown_types = child.allowed_types - all_defined_types
            if unknown_types:
                log_warn(
                    f"{group_type}: category '{child.key}' references types without explicit "
                    f"GroupTypeDefinition: {sorted(unknown_types)}"
                )


COURSE_NUMBER_PREFIX = re.compile(r"^\s*PBS\s+CH\s+", re.IGNORECASE)
# Corona-Kurse 2020/21 haben den Zusatz "C-19", z.B. "PBS CH AG 221-20 C-19"
COURSE_NUMBER_COVID_SUFFIX = re.compile(r"\s+C-19\s*$", re.IGNORECASE)


def shorten_course_number(number: str | None) -> str | None:
    """'PBS CH AG 251-26' -> 'AG251-26', 'PBS CH AG 221-20 C-19' -> 'AG221-20'. Andere Nummern bleiben unverändert."""
    if not number:
        return None
    if not COURSE_NUMBER_PREFIX.match(number):
        return number.strip()
    number = COURSE_NUMBER_COVID_SUFFIX.sub("", number)
    return re.sub(r"\s+", "", COURSE_NUMBER_PREFIX.sub("", number))


def fetch_event_infos(
    midata_service: MidataAPIService,
    group_ids: set[int],
) -> dict[int, dict[str, Any] | None]:
    """Lädt alle EVENTS_TO_SYNC der gegebenen Gruppen parallel. Key ist die event_id."""
    events = [e for e in EVENTS_TO_SYNC if e["group_id"] in group_ids]

    def fetch(event: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return midata_service.get_event_info(event["event_id"], event["group_id"])
        except Exception as e:
            log_error(f"import: Error fetching event ID {event['event_id']}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=MIDATA_FETCH_WORKERS) as executor:
        return dict(zip((e["event_id"] for e in events), executor.map(fetch, events)))


def get_group_events_info(
    group_id: int,
    event_infos: dict[int, dict[str, Any] | None],
) -> list[dict[str, Any]]:
    try:
        matching = [e for e in EVENTS_TO_SYNC if e["group_id"] == group_id]
        if not matching:
            return []

        events_info = []

        for event in matching:
            event_info = event_infos.get(event["event_id"])
            if not event_info:
                log_warn(f"Could not fetch info for event ID {event['event_id']}")
                continue

            event_type = event_info.get("attributes", {}).get("type", "default") 
            event_name_from_api = event_info.get("attributes", {}).get("name")
            # Nur Kurse (type "courses") haben eine Kursnummer, z.B. "PBS CH AG 251-26"
            event_number_from_api = shorten_course_number(event_info.get("attributes", {}).get("number"))

            event_group_name = (
                event.get("short_name")
                or event_number_from_api
                or event_name_from_api
                or f"Event {event_info.get('id')}"
            )

            events_info.append({
                "id": event_info.get("id"),
                "type": event_type,
                "name": event_group_name,
                "group_id": group_id,
                "comment": event.get("comment"),
            })

        return events_info

    except Exception as e:
        log_error(f"import: Error fetching events for group ID {group_id}: {e}")
        return []

def get_effective_role_groups_for_group(node: dict[str, Any]) -> list[str]:
    group_id = node.get("id")
    group_type = node.get("type")

    definition = get_group_definition_or_fallback(group_type)
    allowed_roles = set(definition.allowed_roles)
    default_roles = set(definition.default_roles)

    override = ROLE_GROUP_OVERRIDES.get(group_id, {})
    whitelist = set(override.get("whitelist", set()))
    blacklist = set(override.get("blacklist", set()))

    invalid_whitelist = whitelist - allowed_roles
    if invalid_whitelist:
        log_warn(
            f"Group ID {group_id} ({node.get('name')}): whitelist contains roles not allowed "
            f"for type {group_type}: {sorted(invalid_whitelist)}"
        )

    invalid_blacklist = blacklist - allowed_roles
    if invalid_blacklist:
        log_warn(
            f"Group ID {group_id} ({node.get('name')}): blacklist contains roles not allowed "
            f"for type {group_type}: {sorted(invalid_blacklist)}"
        )

    effective_roles = (default_roles - blacklist) | (whitelist & allowed_roles)
    effective_roles &= allowed_roles

    return sorted(effective_roles)


def upsert_role_subgroups(
    keycloak_service: KeycloakApiService,
    real_group_id: str,
    node: dict[str, Any],
) -> None:
    roles_container_id = keycloak_service.upsert_group(
        parent_id=real_group_id,
        name=ROLE_SUBGROUP_NAME,
        attributes=KeycloakApiService.kc_attr(
            node_kind="category",
            category_key="roles",
        ),
    )

    if not roles_container_id:
        log_error(
            f"Could not create roles subgroup container for group "
            f"{node.get('name')} ({node.get('id')})"
        )
        return

    effective_roles = get_effective_role_groups_for_group(node)

    # Rollen-Container wird immer erstellt, auch wenn effective_roles leer ist.
    for role_value in effective_roles:
        role_name = role_value.split("::")[-1]

        subgroup_id = keycloak_service.upsert_group(
            parent_id=roles_container_id,
            name=role_name,
            attributes=KeycloakApiService.kc_attr(
                node_kind="role",
                role_value=role_value,
                group_id=node.get("id"),
                group_type=node.get("type"),
            ),
        )

        if not subgroup_id:
            log_warn(
                f"Could not create role subgroup '{role_name}' for group "
                f"{node.get('name')} ({node.get('id')})"
            )

def get_collections_for_group(node: dict[str, Any]) -> tuple[CollectionDefinition, ...]:
    definition = get_group_definition_or_fallback(node.get("type"))
    collections = definition.collections + COLLECTION_GROUPS.get(node.get("id"), ())

    # Gruppenspezifische Sammlungen überschreiben solche mit gleichem Key aus dem Gruppentyp
    by_key: dict[str, CollectionDefinition] = {}
    for collection in collections:
        by_key[collection.key] = collection
    return tuple(by_key.values())


def upsert_collection_groups(
    keycloak_service: KeycloakApiService,
    real_group_id: str,
    node: dict[str, Any],
) -> None:
    collections = get_collections_for_group(node)
    if not collections:
        return

    collections_folder_id = keycloak_service.upsert_group(
        parent_id=real_group_id,
        name=COLLECTION_SUBGROUP_NAME,
        attributes=KeycloakApiService.kc_attr(
            node_kind="category",
            category_key="collections",
        ),
    )

    if not collections_folder_id:
        log_error(
            f"Could not create collections folder for group "
            f"{node.get('name')} ({node.get('id')})"
        )
        return

    for collection in collections:
        collection_group_id = keycloak_service.upsert_group(
            parent_id=collections_folder_id,
            name=collection.label,
            attributes=KeycloakApiService.kc_attr(
                node_kind="collection",
                collection_key=collection.key,
                collection_roles=sorted(collection.roles),
            ),
        )

        if not collection_group_id:
            log_warn(
                f"Could not create collection '{collection.label}' for group "
                f"{node.get('name')} ({node.get('id')})"
            )


def upsert_event_groups(
    keycloak_service: KeycloakApiService,
    real_group_id: str,
    node: dict[str, Any],
) -> None:
    events = node.get("events") or []
    if not events:
        return

    events_folder_id = keycloak_service.upsert_group(
        parent_id=real_group_id,
        name="Anlässe",
        attributes=KeycloakApiService.kc_attr(
            node_kind="category",
            category_key="events",
        ),
    )

    if not events_folder_id:
        log_error(
            f"Could not create events folder for group "
            f"{node.get('name')} ({node.get('id')})"
        )
        return

    for event in events:
        event_id = event.get("id")
        event_name = event.get("name")
        event_type = event.get("type")

        if event_id is None or not event_name:
            log_warn(f"Skipping invalid event entry: {event}")
            continue

        event_definition = get_event_definition(event_type)

        event_group_id = keycloak_service.upsert_group(
            parent_id=events_folder_id,
            name=event_name,
            attributes=KeycloakApiService.kc_attr(
                node_kind="event",
                event_id=event_id,
                event_type=event_type or "default",
                source_group_id=node.get("id"),
                comment=event.get("comment"),
            ),
        )

        if not event_group_id:
            log_warn(
                f"Could not create event group '{event_name}' "
                f"for group {node.get('name')} ({node.get('id')})"
            )
            continue

        upsert_event_role_categories(
            keycloak_service=keycloak_service,
            event_group_id=event_group_id,
            event=event,
            event_definition=event_definition,
        )
        
def upsert_event_role_categories(
    keycloak_service: KeycloakApiService,
    event_group_id: str,
    event: dict[str, Any],
    event_definition: EventTypeDefinition,
) -> None:
    # Die Teilnahmen werden beim Login vom Keycloak-Mapper direkt aus MIDATA geladen.
    # Hier werden nur die Rollen pro Kategorie hinterlegt.
    for category in event_definition.categories:
        category_group_id = keycloak_service.upsert_group(
            parent_id=event_group_id,
            name=category.label,
            attributes=KeycloakApiService.kc_attr(
                node_kind="category",
                category_key=category.key,
                event_roles=sorted(category.event_roles),
                event_type=event_definition.type_key,
            ),
            remove_attributes={"participant_ids"},
        )

        if not category_group_id:
            log_warn(
                f"Could not create event category '{category.label}' "
                f"for event {event.get('name')} ({event.get('id')})"
            )

def import_group_tree_to_keycloak(
    node: dict[str, Any],
    parent_group_id: str,
    keycloak_service: KeycloakApiService,
    midata_service: MidataAPIService,
) -> str | None:
    node_name = node.get("name")
    node_id = node.get("id")
    node_type = node.get("type")

    if not node_name or node_id is None or not node_type:
        log_error(f"Invalid node encountered (missing name/id/type): {node}")
        return None

    definition = get_group_definition_or_fallback(node_type)

    try:
        real_group_id = keycloak_service.upsert_group(
            parent_id=parent_group_id,
            name=node_name,
            attributes=KeycloakApiService.kc_attr(
                group_id=node_id,
                group_type=node_type,
                node_kind="real",
            ),
        )

        if not real_group_id:
            log_warn(
                f"Skipping recursion because real group could not be created or resolved: "
                f"{node_name} ({node_id})"
            )
            return None

        # Rollen-Container IMMER erstellen
        upsert_role_subgroups(
            keycloak_service=keycloak_service,
            real_group_id=real_group_id,
            node=node,
        )
        
        upsert_event_groups(
            keycloak_service=keycloak_service,
            real_group_id=real_group_id,
            node=node,
        )

        upsert_collection_groups(
            keycloak_service=keycloak_service,
            real_group_id=real_group_id,
            node=node,
        )

        # Kategorien aus GroupDefinition ableiten
        for child_def in definition.children:
            items = node.get(child_def.key) or []
            if not items:
                continue

            target_parent_id = real_group_id

            if child_def.create_folder_in_keycloak:
                folder_id = keycloak_service.upsert_group(
                    parent_id=real_group_id,
                    name=child_def.label,
                    attributes=KeycloakApiService.kc_attr(
                        node_kind="category",
                        category_key=child_def.key,
                    ),
                )

                if not folder_id:
                    log_error(
                        f'Could not create category folder "{child_def.label}" under "{node_name}". '
                        f"Skipping its children."
                    )
                    continue

                target_parent_id = folder_id

            for child in items:
                import_group_tree_to_keycloak(
                    node=child,
                    parent_group_id=target_parent_id,
                    keycloak_service=keycloak_service,
                    midata_service=midata_service,
                )

        # unbekannte Kinder optional loggen
        unknown_children = node.get("unknown_children") or []
        if unknown_children:
            log_warn(
                f"Group '{node_name}' ({node_type}) contains {len(unknown_children)} unknown children "
                f"that were not imported. [Types: {sorted({c.get('type') for c in unknown_children if c.get('type')})}]" 
            )

        return real_group_id

    except Exception as e:
        log_error(
            f"Failed to import node to Keycloak "
            f"(id={node_id}, name={node_name}, type={node_type}): {e}"
        )
        return None

def enrich_tree_with_events(
    node: dict[str, Any],
    event_infos: dict[int, dict[str, Any] | None],
) -> dict[str, Any]:
    group_id = node.get("id")
    if group_id is None:
        return node

    node["events"] = get_group_events_info(group_id, event_infos)

    definition = get_group_definition_or_fallback(node.get("type"))
    for child_def in definition.children:
        items = node.get(child_def.key) or []
        for child in items:
            enrich_tree_with_events(child, event_infos)

    # unknown_children optional auch mitnehmen
    for child in node.get("unknown_children") or []:
        enrich_tree_with_events(child, event_infos)

    return node

def write_json_file(filename: str, data: Any) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    start_time = time.perf_counter()

    config = parse_env()
    validate_group_definitions()

    keycloak_service = KeycloakApiService(
        config["keycloak_url"],
        config["keycloak_realm"],
        config["keycloak_user_realm"],
        config["keycloak_username"],
        config["keycloak_password"],
    )

    midata_service = MidataAPIService(
        config["midata_url"],
        config["midata_token"],
        max_connections=MIDATA_FETCH_WORKERS,
    )

    # Keycloak root
    root_kc_id = ensure_keycloak_root(keycloak_service, KEYCLOAK_GROUP_ROOT)
    log_info(f"Using Keycloak root '{KEYCLOAK_GROUP_ROOT}' ({now_s(start_time)})")

    # MIDATA Gruppenliste einmal laden
    all_groups = fetch_midata_group_list(config["midata_url"], config["midata_token"])
    children_by_parent = build_group_children_index(all_groups)
    groups_by_id = {g["id"]: g for g in all_groups}

    raw_roots: list[dict[str, Any]] = []
    categorized_roots: list[dict[str, Any]] = []
    
    build_hierarchy_from_midata = True
    
    if not RECREATE_HIRARCHY:
        log_info(f"Recreate hierarchy is disabled. ({now_s(start_time)})")
        # Check if the json files exist then load them instead of building the hierarchy from MIDATA
        if os.path.isfile(RAW_ROOTS_JSON_FILE) and os.path.isfile(CATEGORIZED_ROOTS_JSON_FILE):
            log_info(f"Loading raw roots from {RAW_ROOTS_JSON_FILE}")
            with open(RAW_ROOTS_JSON_FILE, "r", encoding="utf-8") as f:
                raw_roots = json.load(f)

            log_info(f"Loading categorized roots from {CATEGORIZED_ROOTS_JSON_FILE}")
            with open(CATEGORIZED_ROOTS_JSON_FILE, "r", encoding="utf-8") as f:
                categorized_roots = json.load(f)
            build_hierarchy_from_midata = False
        else:
            log_warn(
                f"Raw roots or categorized roots JSON files not found. Building hierarchy from MIDATA "
                f"data instead. ({now_s(start_time)})"
            )
            build_hierarchy_from_midata = True
    
    if build_hierarchy_from_midata:
        for root_id in MIDATA_ROOT_GROUP_IDS:
            root_group = groups_by_id.get(root_id)
            if not root_group:
                log_warn(f"Root group with ID {root_id} not found in MIDATA group list. Skipping.")
                continue

            log_info(f"Building hierarchy for root ID {root_id}")
            subtree_ids = collect_subtree_ids(root_id, children_by_parent)
            group_names = fetch_group_names(midata_service, subtree_ids)
            log_info(f"Fetched {len(group_names)} group names ({now_s(start_time)})")

            raw_tree = build_raw_tree(root_group, children_by_parent, group_names, is_root=True)
            raw_roots.append(raw_tree)

            event_infos = fetch_event_infos(midata_service, set(subtree_ids))
            log_info(f"Fetched {len(event_infos)} events ({now_s(start_time)})")

            categorized_tree = categorize_group_tree(raw_tree)
            categorized_tree = enrich_tree_with_events(categorized_tree, event_infos)
            categorized_roots.append(categorized_tree)

        write_json_file(RAW_ROOTS_JSON_FILE, raw_roots)
        write_json_file(CATEGORIZED_ROOTS_JSON_FILE, categorized_roots)

        log_info(f"Wrote {RAW_ROOTS_JSON_FILE} and {CATEGORIZED_ROOTS_JSON_FILE} ({now_s(start_time)})")

    # Keycloak Token laden
    keycloak_service.token = keycloak_service.get_token()

    # Alle Roots unter dem konfigurierten Root importieren
    for root in categorized_roots:
        import_group_tree_to_keycloak(
            node=root,
            parent_group_id=root_kc_id,
            keycloak_service=keycloak_service,
            midata_service=midata_service,
        )

    log_info(f"Import finished ({now_s(start_time)})")


if __name__ == "__main__":
    main()