"""
assign-roles.py

Bulk-assigns a Keycloak (realm or client) role to all matching subgroups
under a given MIDATA group subtree - either role subgroups (e.g. every
"Webmaster" group) or category container folders (e.g. every "Rollen"
folder itself).

Independent of the import script - it only talks to Keycloak. It relies
on the group attributes the import script already writes via
KeycloakApiService.kc_attr(...):

    node_kind     = "real" | "category" | "role" | "event"
    role_value    = e.g. "Group::Abteilung::Webmaster"   (only for node_kind == "role")
    category_key  = e.g. "roles" (the "Rollen" folder) or "events" (the "Anlässe" folder)
                    (only for node_kind == "category")
    group_id      = the MIDATA group id                  (only for node_kind == "real")

Match a specific role subgroup - by its short Keycloak name:
    python assign-roles.py --midata-group-id 5411 --role-name Webmaster --keycloak-role mike.leader

... or by the full role_value (matches the same groups, just a different way to specify it):
    python assign-roles.py --midata-group-id 5411 --role-value "Group::Abteilung::Webmaster" --keycloak-role mike.leader

Match a category container folder instead (e.g. the "Rollen" folder itself,
rather than the role subgroups inside it):
    python assign-roles.py --midata-group-id 5411 --category-key roles --keycloak-role mike.leader

Assign a client role instead of a realm role:
    python assign-roles.py --midata-group-id 5411 --role-name Webmaster --keycloak-role app-viewer --client-id my-client

Preview matches without changing anything:
    python assign-roles.py --midata-group-id 5411 --role-name Webmaster --keycloak-role mike.leader --dry-run

--role-name, --role-value, and --category-key are mutually exclusive -
pick exactly one way to identify which groups to target.

Requires the same .env variables as the import script:
    KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_USER_REALM,
    KEYCLOAK_USERNAME, KEYCLOAK_PASSWORD
"""

import argparse
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.KeycloakApiService import KeycloakApiService  # noqa: E402

load_dotenv()


def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")


def log_warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}")


def parse_env() -> dict[str, str]:
    required_vars = [
        "KEYCLOAK_URL",
        "KEYCLOAK_REALM",
        "KEYCLOAK_USER_REALM",
        "KEYCLOAK_USERNAME",
        "KEYCLOAK_PASSWORD",
    ]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return {
        "keycloak_url": os.getenv("KEYCLOAK_URL", ""),
        "keycloak_realm": os.getenv("KEYCLOAK_REALM", ""),
        "keycloak_user_realm": os.getenv("KEYCLOAK_USER_REALM", ""),
        "keycloak_username": os.getenv("KEYCLOAK_USERNAME", ""),
        "keycloak_password": os.getenv("KEYCLOAK_PASSWORD", ""),
    }


class KeycloakRoleService(KeycloakApiService):
    """
    Extends KeycloakApiService with the group-lookup and role-mapping
    calls needed for bulk role assignment. Reuses the parent's
    authenticated _request() (incl. 401 token refresh).
    """

    # --------- group lookup by MIDATA attributes ---------

    def find_group_by_midata_id(self, midata_group_id: int) -> dict | None:
        """
        Breadth-first search over the whole group tree for the group
        whose attributes have node_kind=real and group_id=<midata_group_id>.
        """
        frontier = self.get_groups()
        target = str(midata_group_id)

        while frontier:
            next_frontier = []
            for g in frontier:
                full = self.get_group(g["id"])
                attrs = full.get("attributes") or {}
                if attrs.get("node_kind") == ["real"] and attrs.get("group_id") == [target]:
                    return full
                next_frontier.extend(self.get_group_children(g["id"]))
            frontier = next_frontier

        return None

    def find_subgroups(
        self,
        root_group_id: str,
        *,
        node_kind: str | None = None,
        role_name: str | None = None,
        role_value: str | None = None,
        category_key: str | None = None,
    ) -> list[dict]:
        """
        Walks the subtree under root_group_id and returns every group matching
        the given criteria. At least one of role_name / role_value / category_key
        must be given (node_kind alone would match everything and is easy to
        fat-finger into assigning a role far too broadly).

          - role_name:    group's short Keycloak name, e.g. "Adressverwaltung"
                           (implies node_kind == "role" unless overridden)
          - role_value:   full role_value attribute, e.g. "Group::Abteilung::Adressverwaltung"
                           (implies node_kind == "role" unless overridden)
          - category_key: category_key attribute, e.g. "roles" for the "Rollen"
                           container itself, or "events" for "Anlässe"
                           (implies node_kind == "category" unless overridden)
        """
        if not (role_name or role_value or category_key):
            raise ValueError("Pass at least one of role_name, role_value, or category_key.")

        if node_kind is None:
            node_kind = "category" if category_key else "role"

        matches: list[dict] = []
        frontier = self.get_group_children(root_group_id)

        while frontier:
            next_frontier = []
            for child in frontier:
                full = self.get_group(child["id"])
                attrs = full.get("attributes") or {}
                child_node_kind = (attrs.get("node_kind") or [None])[0]
                child_role_value = (attrs.get("role_value") or [None])[0]
                child_category_key = (attrs.get("category_key") or [None])[0]

                match = child_node_kind == node_kind
                if role_name is not None:
                    match = match and full.get("name") == role_name
                if role_value is not None:
                    match = match and child_role_value == role_value
                if category_key is not None:
                    match = match and child_category_key == category_key

                if match:
                    matches.append(full)

                next_frontier.extend(self.get_group_children(child["id"]))
            frontier = next_frontier

        return matches

    # --------- roles ---------

    def get_realm_role(self, role_name: str) -> dict | None:
        r = self._request("GET", f"{self._admin_base()}/roles/{role_name}", timeout=30)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def get_client_uuid(self, client_id: str) -> str | None:
        r = self._request("GET", f"{self._admin_base()}/clients", params={"clientId": client_id}, timeout=30)
        r.raise_for_status()
        clients = r.json()
        return clients[0]["id"] if clients else None

    def get_client_role(self, client_uuid: str, role_name: str) -> dict | None:
        r = self._request("GET", f"{self._admin_base()}/clients/{client_uuid}/roles/{role_name}", timeout=30)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    # --------- group role mappings ---------

    def get_group_role_mappings(self, group_id: str, client_uuid: str | None = None) -> list[dict]:
        if client_uuid:
            url = f"{self._admin_base()}/groups/{group_id}/role-mappings/clients/{client_uuid}"
        else:
            url = f"{self._admin_base()}/groups/{group_id}/role-mappings/realm"
        r = self._request("GET", url, timeout=30)
        r.raise_for_status()
        return r.json()

    def assign_group_role(self, group_id: str, role_repr: dict, client_uuid: str | None = None) -> None:
        if client_uuid:
            url = f"{self._admin_base()}/groups/{group_id}/role-mappings/clients/{client_uuid}"
        else:
            url = f"{self._admin_base()}/groups/{group_id}/role-mappings/realm"
        r = self._request("POST", url, json_body=[role_repr], timeout=30)
        r.raise_for_status()


def assign_role_to_group(
    keycloak_service: KeycloakRoleService,
    group: dict,
    role_repr: dict,
    client_uuid: str | None,
    dry_run: bool,
) -> bool:
    group_id = group["id"]
    group_name = group.get("name", "?")

    if dry_run:
        log_info(f"[dry-run] Would assign role to '{group_name}' ({group_id})")
        return True

    existing = keycloak_service.get_group_role_mappings(group_id, client_uuid)
    if any(r.get("id") == role_repr.get("id") for r in existing):
        log_info(f"Role already assigned to '{group_name}' ({group_id}), skipping.")
        return True

    keycloak_service.assign_group_role(group_id, role_repr, client_uuid)
    log_info(f"Assigned role to '{group_name}' ({group_id})")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk-assign a Keycloak role to all matching role subgroups under a MIDATA group subtree."
    )
    parser.add_argument("--midata-group-id", type=int, required=True, help="MIDATA root group id, e.g. 5411")

    role_group = parser.add_mutually_exclusive_group(required=True)
    role_group.add_argument(
        "--role-name",
        help='Match role subgroups by short Keycloak name, e.g. "Webmaster"',
    )
    role_group.add_argument(
        "--role-value",
        help='Match role subgroups by the full role_value attribute, e.g. "Group::Abteilung::Webmaster"',
    )
    role_group.add_argument(
        "--category-key",
        help='Match category container folders, e.g. "roles" for the "Rollen" folder itself, '
        'or "events" for "Anlässe"',
    )

    parser.add_argument("--keycloak-role", required=True, help="Name of the Keycloak role to assign")
    parser.add_argument("--client-id", default=None, help="If set, assign a client role instead of a realm role")
    parser.add_argument("--dry-run", action="store_true", help="List matching groups without assigning anything")
    args = parser.parse_args()

    config = parse_env()

    keycloak_service = KeycloakRoleService(
        config["keycloak_url"],
        config["keycloak_realm"],
        config["keycloak_user_realm"],
        config["keycloak_username"],
        config["keycloak_password"],
    )

    client_uuid = None
    if args.client_id:
        client_uuid = keycloak_service.get_client_uuid(args.client_id)
        if not client_uuid:
            log_error(f"Client '{args.client_id}' not found in realm.")
            sys.exit(1)
        role_repr = keycloak_service.get_client_role(client_uuid, args.keycloak_role)
    else:
        role_repr = keycloak_service.get_realm_role(args.keycloak_role)

    if not role_repr:
        scope = f"client '{args.client_id}'" if args.client_id else "realm"
        log_error(f"Role '{args.keycloak_role}' not found on {scope}.")
        sys.exit(1)

    root_group = keycloak_service.find_group_by_midata_id(args.midata_group_id)
    if not root_group:
        log_error(f"No Keycloak group found for MIDATA group id {args.midata_group_id}.")
        sys.exit(1)

    log_info(
        f"Resolved MIDATA group {args.midata_group_id} -> "
        f"Keycloak group '{root_group['name']}' ({root_group['id']})"
    )

    matches = keycloak_service.find_subgroups(
        root_group["id"],
        role_name=args.role_name,
        role_value=args.role_value,
        category_key=args.category_key,
    )
    match_label = args.role_name or args.role_value or args.category_key
    if not matches:
        log_warn(f"No subgroups matching '{match_label}' found under group {args.midata_group_id}.")
        return

    log_info(f"Found {len(matches)} group(s) matching '{match_label}'. Assigning role '{args.keycloak_role}'...")

    success_count = 0
    for group in matches:
        try:
            ok = assign_role_to_group(keycloak_service, group, role_repr, client_uuid, args.dry_run)
        except Exception as e:
            log_error(f"Failed to assign role to '{group.get('name')}' ({group['id']}): {e}")
            ok = False
        success_count += int(ok)

    log_info(f"Done. {success_count}/{len(matches)} groups processed successfully.")


if __name__ == "__main__":
    main()