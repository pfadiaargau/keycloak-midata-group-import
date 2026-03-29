import json
import os
import time
from collections import defaultdict
from typing import Any

import requests
from dotenv import load_dotenv

from model.GroupDefinitions import GROUP_DEFINITIONS
from model.groups.MidataGroups import MidataGroups
from model.roles.abteilung import AbteilungRoles
from model.types.GroupTypeDefinition import GroupTypeDefinition
from services.KeycloakApiService import KeycloakApiService
from services.MidataApiService import MidataAPIService

load_dotenv()

KEYCLOAK_GROUP_ROOT = os.getenv("KEYCLOAK_GROUP_ROOT", "midata")

# Mehrere Startknoten statt nur ein Root
MIDATA_ROOT_GROUP_IDS = [
    int(x.strip())
    for x in os.getenv("MIDATA_ROOT_GROUP_IDS").split(",")
    if x.strip()
]

# Rollen-Container wird immer erzeugt
ROLE_SUBGROUP_NAME = "Rollen"

# Optional: Events
EVENTS_TO_SYNC = [
    # {"group_id": 400, "event_id": 2688, "short_name": "AG-111-26"},
]

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



def build_raw_tree(
    root_group: dict[str, Any],
    children_by_parent: dict[int | None, list[dict[str, Any]]],
    midata_service: MidataAPIService,
    *,
    is_root: bool = False,
    parent_id: int | None = None,
) -> dict[str, Any] | None:
    node = dict(root_group)

    try:
        node["name"] = fetch_group_name(midata_service, node["id"])
    except Exception as e:
        msg = (
            f"group_id={node.get('id')}, "
            f"type={node.get('type')}, "
            f"parent_id={parent_id}: {e}"
        )

        if is_root:
            raise RuntimeError(f"Configured root group is invalid: {msg}") from e

        log_warn(f"Skipping node: {msg}")
        return None

    children = children_by_parent.get(node["id"], [])
    node["children"] = [
        child_node
        for child_node in (
            build_raw_tree(
                child,
                children_by_parent,
                midata_service,
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


def validate_group_definitions() -> None:
    all_defined_types = set(GROUP_DEFINITIONS.keys())

    for group_type, definition in GROUP_DEFINITIONS.items():
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


def get_group_events_info(group_id: int, midata_service: MidataAPIService) -> list[dict[str, Any]]:
    try:
        matching = [e for e in EVENTS_TO_SYNC if e["group_id"] == group_id]
        if not matching:
            return []

        events_info = []
        for event in matching:
            event_info = midata_service.get_event_info(event["event_id"])
            if not event_info:
                log_warn(f"Could not fetch info for event ID {event['event_id']}")
                continue

            events_info.append({
                "id": event_info["id"],
                "short_name": event["short_name"],
                "type": event_info.get("attributes", {}).get("type"),
                "name": event["short_name"],
            })
        return events_info
    except Exception as e:
        log_error(f"Error fetching events for group ID {group_id}: {e}")
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


def import_group_tree_to_keycloak(
    node: dict[str, Any],
    parent_group_id: str,
    keycloak_service: KeycloakApiService,
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
    
    for root_id in MIDATA_ROOT_GROUP_IDS:
        root_group = groups_by_id.get(root_id)
        if not root_group:
            log_warn(f"Root group with ID {root_id} not found in MIDATA group list. Skipping.")
            continue

        log_info(f"Building hierarchy for root ID {root_id}")
        raw_tree = build_raw_tree(root_group, children_by_parent, midata_service)
        raw_roots.append(raw_tree)

        categorized_tree = categorize_group_tree(raw_tree)

        # Optional Events pro Root-Knoten oder rekursiv später einbauen
        categorized_roots.append(categorized_tree)

    # write_json_file("detailed_hierarchy.json", raw_roots)
    # write_json_file("categorized_groups.json", categorized_roots)

    # log_info(f"Wrote detailed_hierarchy.json and categorized_groups.json ({now_s(start_time)})")

    # Keycloak Token laden
    keycloak_service.token = keycloak_service.get_token()

    # Alle Roots unter dem konfigurierten Root importieren
    for root in categorized_roots:
        import_group_tree_to_keycloak(
            node=root,
            parent_group_id=root_kc_id,
            keycloak_service=keycloak_service,
        )

    log_info(f"Import finished ({now_s(start_time)})")


if __name__ == "__main__":
    main()