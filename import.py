import json
import os

import requests
from dotenv import load_dotenv

from model.GroupType import GroupType
from services.KeycloakApiService import KeycloakApiService
from services.MidataApiService import MidataAPIService
from strings.SubgroupLabels import CATEGORY_LABELS

KEYCLOAK_GROUP_ROOT = os.getenv("KEYCLOAK_GROUP_ROOT", "midata")

MIDATA_ROOT_GROUP_ID = int(os.getenv("MIDATA_ROOT_GROUP_ID", 4691))


def main():
    start_time = os.times()
    load_dotenv()
    midata_token = os.getenv("MIDATA_SERVICE_ACCOUNT_TOKEN")
    midata_url = os.getenv("MIDATA_URL")

    keycloak_url = os.getenv("KEYCLOAK_URL")
    keycloak_realm = os.getenv("KEYCLOAK_REALM")
    keycloak_user_realm = os.getenv("KEYCLOAK_USER_REALM")
    keycloak_username = os.getenv("KEYCLOAK_USERNAME")
    keycloak_password = os.getenv("KEYCLOAK_PASSWORD")
    
    KEYCLOAK_SERVICE = KeycloakApiService(keycloak_url, keycloak_realm, keycloak_user_realm, keycloak_username, keycloak_password)
    
    MIDATA_SERVICE = MidataAPIService(midata_url, midata_token)

    midata_headers = {
        "X-Token": midata_token,
        "Content-Type": "application/json"
    }

    # To allow multiple IDPs or similar solutions a root group should be defined which is created in the following step
    try:
        if not KEYCLOAK_SERVICE.check_keycloak_group_path(KEYCLOAK_GROUP_ROOT.split("/")):
            print(f"Keycloak group path {KEYCLOAK_GROUP_ROOT} does not exist.")
            KEYCLOAK_SERVICE.create_group_path(KEYCLOAK_GROUP_ROOT.split("/"))
            print(f"Keycloak group path {KEYCLOAK_GROUP_ROOT} has been created. ({os.times()[4] - start_time[4]:.2f} seconds)")
        else:
            print(f"Keycloak group path {KEYCLOAK_GROUP_ROOT} already exists.")
    except:
        print("An error occurred while checking or creating Keycloak root group path.")
        
    # Fetch the hirarchy of groups from midata
    sorted_hirarchy = {}
    try:
        hirarchy_response = requests.get(f"{midata_url}/list_groups", headers=midata_headers)
        hirarchy_response.raise_for_status()
        hirarchy = hirarchy_response.json()["groups"]
        
        root_group: dict = next((g for g in hirarchy if g["id"] == MIDATA_ROOT_GROUP_ID), None) 
        if root_group:
            def sort_hirarchy(group):
                group_info = MIDATA_SERVICE.get_group_info(group["id"])
                if not group_info:
                    print(f"Error fetching group info for group ID {group['id']}")
                    return None
                group_info = group_info.get("attributes", {})
                group["name"] = group_info.get("name")
                children = [g for g in hirarchy if g["parent_id"] == group["id"]]
                group["children"] = [child for child in (sort_hirarchy(child) for child in children) if child is not None]
                return group
            
            sorted_hirarchy = sort_hirarchy(root_group)
            
            with open("detailed_hirarchy.json", "w") as f:
                json.dump(sorted_hirarchy, f, indent=2)
            print("Group hierarchy has been successfully written to detailed_hirarchy.json ({:.2f} seconds)".format(os.times()[4] - start_time[4]))
        else:
            print(f"Error: Root group with ID {MIDATA_ROOT_GROUP_ID} not found in midata groups.")
    except:
        print("An error occurred while fetching the group hierarchy from midata.")

    # Categorize the groups by their type and write them to a file
    categorized_groups = {}
    
    def categorize_groups(group):
        # --- define committee type sets ---
        KANTONAL_COMMITTEES = {
            GroupType.KANTONALES_GREMIUM.value,
            GroupType.INTERNES_KANTONALES_GREMIUM.value,
        }
        REGIONAL_COMMITTEES = {
            GroupType.REGIONALES_GREMIUM.value,
            GroupType.INTERNES_REGIONALES_GREMIUM.value,
        }
        ABTEILUNG_COMMITTEES = {
            GroupType.ABTEILUNGS_GREMIUM.value,
            GroupType.INTERNES_ABTEILUNGS_GREMIUM.value,
        }
        ALL_COMMITTEES = KANTONAL_COMMITTEES | REGIONAL_COMMITTEES | ABTEILUNG_COMMITTEES

        # Helper: is this child a committee (of any level)?
        def is_committee(node: dict) -> bool:
            return node.get("type") in ALL_COMMITTEES

        t = group.get("type")

        # --- KANTONALVERBAND ---
        if t == GroupType.KANTONALVERBAND.value:
            group["scout_groups"] = []
            group["committees"] = []
            group["regions"] = []

            for child in group.get("children", []):
                if is_committee(child):
                    group["committees"].append(child)
                elif child["type"] == GroupType.ABTEILUNG.value:
                    group["scout_groups"].append(child)
                elif child["type"] == GroupType.REGION.value:
                    group["regions"].append(child)

        # --- REGION ---
        elif t == GroupType.REGION.value:
            group["scout_groups"] = []
            group["committees"] = []
            group["agegroups"] = []

            for child in group.get("children", []):
                if is_committee(child):
                    group["committees"].append(child)
                elif child["type"] in {GroupType.REGIONALE_ROVER.value}:
                    group["agegroups"].append(child)
                elif child["type"] == GroupType.ABTEILUNG.value:
                    group["scout_groups"].append(child)

        # --- ABTEILUNG ---
        elif t == GroupType.ABTEILUNG.value:
            group["agegroups"] = []
            group["committees"] = []

            for child in group.get("children", []):
                if is_committee(child):
                    group["committees"].append(child)
                elif child["type"] in {
                    GroupType.BIBER.value,
                    GroupType.WOELFE.value,
                    GroupType.PFADI.value,
                    GroupType.PIO.value,
                    GroupType.ABTEILUNGS_ROVER.value,
                }:
                    group["agegroups"].append(child)

        # --- AGEGROUP ---
        elif t in {
            GroupType.BIBER.value,
            GroupType.WOELFE.value,
            GroupType.PFADI.value,
            GroupType.PIO.value,
            GroupType.ABTEILUNGS_ROVER.value,
            GroupType.REGIONALE_ROVER.value,  # keep consistent if this is also an agegroup-like node
        }:
            group["agegroup_responsibles"] = []
            group["agegroup_leaders"] = []
            group["agegroup_participants"] = []

        # --- COMMITTEE (stacking) ---
        # IMPORTANT: committees can contain committees directly; no subgroup folder required.
        if is_committee(group):
            group.setdefault("committees", [])

            # Put nested committees straight into this committee node
            for child in group.get("children", []):
                if is_committee(child):
                    group["committees"].append(child)

            # If you ever also want to keep non-committee children under committees,
            # you can add more buckets here (optional). For now we focus on committee stacking.

        # --- recurse for ALL children (so committee children get processed too) ---
        for child in group.get("children", []):
            categorize_groups(child)

        # Remove raw children after categorization
        if "children" in group:
            del group["children"]

        return group
    categorized_groups = categorize_groups(sorted_hirarchy)
    with open("categorized_groups.json", "w", encoding="utf-8") as f:
        json.dump(categorized_groups, f, indent=2, ensure_ascii=False)
    print("Categorized groups have been successfully written to categorized_groups.json")
    
    
    # Importing the groups to Keycloak

    COMMITTEE_TYPES = {
        GroupType.KANTONALES_GREMIUM.value,
        GroupType.INTERNES_KANTONALES_GREMIUM.value,
        GroupType.REGIONALES_GREMIUM.value,
        GroupType.INTERNES_REGIONALES_GREMIUM.value,
        GroupType.ABTEILUNGS_GREMIUM.value,
        GroupType.INTERNES_ABTEILUNGS_GREMIUM.value,
    }

    def is_committee_node(node: dict) -> bool:
        return node.get("type") in COMMITTEE_TYPES

    def import_group_tree_to_keycloak(node: dict, parent_group_id: str) -> str | None:
        """
        Imports one real group node under parent_group_id.

        Folder behavior:
        - For most categories: create folder groups as usual
        - For 'committees':
            * If CURRENT node is a committee -> DO NOT create a "Committees" folder
                (nested committees go directly under the committee)
            * Otherwise -> create the "Committees" folder like normal
        """
        node_name = node.get("name")
        node_id = node.get("id")
        node_type = node.get("type")

        if not node_name or node_id is None or not node_type:
            print(f"[ERROR] Invalid node encountered (missing name/id/type): {node}")
            return None

        # 1) Upsert the real group
        real_group_id = KEYCLOAK_SERVICE.upsert_group(
            parent_id=parent_group_id,
            name=node_name,
            attributes=KeycloakApiService.kc_attr(
                group_id=node_id,
                group_type=node_type,
                node_kind="real",
            ),
        )

        # If skipped due to duplicate name conflict -> stop recursion
        if not real_group_id:
            return None

        current_is_committee = is_committee_node(node)

        # 2) Recurse categories
        for key, label in CATEGORY_LABELS.items():
            items = node.get(key) or []
            if not items:
                continue

            # Special rule ONLY for committees when the CURRENT node is a committee:
            # -> no "Committees" folder under a committee node
            if key == "committees" and current_is_committee:
                for child in items:
                    import_group_tree_to_keycloak(child, real_group_id)
                continue

            # Default behavior: create folder for this category
            folder_id = KEYCLOAK_SERVICE.upsert_group(
                parent_id=real_group_id,
                name=label,
                attributes=KeycloakApiService.kc_attr(
                    node_kind="category",
                    category_key=key,
                ),
            )

            if not folder_id:
                print(f'[ERROR] Could not create category folder "{label}" under "{node_name}". Skipping its children.')
                continue

            for child in items:
                import_group_tree_to_keycloak(child, folder_id)

        return real_group_id

    try:
        # Resolve / ensure the configured Keycloak root exists (you already created it above)
        root_path = KEYCLOAK_GROUP_ROOT.split("/")
        root_kc_id = KEYCLOAK_SERVICE.get_group_id_by_path(root_path)

        if not root_kc_id:
            raise RuntimeError(f"Could not resolve Keycloak group id for path: {KEYCLOAK_GROUP_ROOT}")

        # Import your categorized tree beneath the root folder
        import_group_tree_to_keycloak(categorized_groups, root_kc_id)

        print(f"Groups have been successfully imported to Keycloak under {KEYCLOAK_GROUP_ROOT}. "
              f"({os.times()[4] - start_time[4]:.2f} seconds)")
    except Exception as e:
        print(f"An error occurred while importing groups to Keycloak: {e}")    
            
    
    
    
def check_env_variables():
    load_dotenv()
    required_vars = [
        "MIDATA_SERVICE_ACCOUNT_TOKEN",
        "MIDATA_URL",

        "KEYCLOAK_URL",
        "KEYCLOAK_REALM",
        "KEYCLOAK_USER_REALM",
        "KEYCLOAK_USERNAME",
        "KEYCLOAK_PASSWORD"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    if check_env_variables():
        main()