import requests


class KeycloakApiService:
    def __init__(self, keycloak_url, keycloak_realm, keycloak_user_realm, keycloak_username, keycloak_password):
        self.keycloak_url = keycloak_url.rstrip("/")
        self.keycloak_realm = keycloak_realm
        self.keycloak_user_realm = keycloak_user_realm
        self.keycloak_username = keycloak_username
        self.keycloak_password = keycloak_password
        self.token = self.get_token()

    # --------- auth ---------

    def get_token(self):
        token_url = f"{self.keycloak_url}/realms/{self.keycloak_user_realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": self.keycloak_username,
            "password": self.keycloak_password
        }
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Keycloak token: {e}")
            return None

    def _headers(self, json: bool = False) -> dict:
        h = {"Authorization": f"Bearer {self.token}"}
        if json:
            h["Content-Type"] = "application/json"
        return h

    def _admin_base(self) -> str:
        return f"{self.keycloak_url}/admin/realms/{self.keycloak_realm}"

    # --------- group attributes helper ---------

    @staticmethod
    def kc_attr(**kwargs) -> dict:
        """
        Keycloak requires group attributes as:
          {"key": ["value"]}
        """
        out = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            # always store as list[str]
            out[k] = [str(v)] if not isinstance(v, list) else [str(x) for x in v]
        return out

    # --------- basic group CRUD ---------

    def get_groups(self, search: str | None = None) -> list:
        """
        GET /groups?search=
        Returns top-level groups (Keycloak may include subGroups in each object).
        """
        params = {}
        if search:
            params["search"] = search

        r = requests.get(f"{self._admin_base()}/groups", headers=self._headers(), params=params)
        r.raise_for_status()
        return r.json()

    def get_group(self, group_id: str) -> dict:
        r = requests.get(f"{self._admin_base()}/groups/{group_id}", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_group_children(self, group_id: str) -> list:
        r = requests.get(f"{self._admin_base()}/groups/{group_id}/children", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def create_group(self, payload: dict, parent_id: str | None = None) -> str:
        """
        Creates a group. If parent_id is None => top-level group.
        Returns created group id (from Location header).
        """
        if parent_id is None:
            url = f"{self._admin_base()}/groups"
        else:
            url = f"{self._admin_base()}/groups/{parent_id}/children"

        r = requests.post(url, headers=self._headers(json=True), json=payload)
        r.raise_for_status()

        loc = r.headers.get("Location", "")
        created_id = loc.rstrip("/").split("/")[-1]
        if not created_id:
            raise RuntimeError("Could not determine created Keycloak group id (missing Location header).")
        return created_id

    def update_group(self, group_id: str, payload: dict) -> None:
        r = requests.put(f"{self._admin_base()}/groups/{group_id}", headers=self._headers(json=True), json=payload)
        r.raise_for_status()

    # --------- lookup helpers ---------

    def find_child_by_name(self, parent_id: str | None, name: str) -> str | None:
        """
        Finds a direct child group by exact name.
        If parent_id is None, searches top-level.
        """
        if parent_id is None:
            # /groups?search= returns top-level groups matching; we match exact name
            candidates = self.get_groups(search=name)
            for g in candidates:
                if g.get("name") == name:
                    return g.get("id")
            return None

        children = self.get_group_children(parent_id)
        for g in children:
            if g.get("name") == name:
                return g.get("id")
        return None

    def get_group_id_by_path(self, group_path: list[str]) -> str | None:
        """
        Walk a path like ["midata", "Pfadi Aargau", "Regions"] and returns the final group id.
        """
        parent_id = None
        for part in group_path:
            gid = self.find_child_by_name(parent_id, part)
            if not gid:
                return None
            parent_id = gid
        return parent_id

    # --------- upsert helper ---------

    def upsert_group(self, parent_id: str | None, name: str, attributes: dict | None = None) -> str | None:
        """
        Create group if missing.
        If group with same name exists under same parent:
            - If same group_id attribute -> update normally
            - If different group_id attribute -> skip and print error
        Returns group id or None if skipped due to conflict.
        """

        existing_id = self.find_child_by_name(parent_id, name)

        if existing_id:
            current = self.get_group(existing_id)
            current_attrs = current.get("attributes") or {}

            existing_group_id = None
            if "group_id" in current_attrs and current_attrs["group_id"]:
                existing_group_id = current_attrs["group_id"][0]

            incoming_group_id = None
            if attributes and "group_id" in attributes and attributes["group_id"]:
                incoming_group_id = attributes["group_id"][0]

            # 🔴 Name collision with different group_id → skip
            if existing_group_id and incoming_group_id and existing_group_id != incoming_group_id:
                print(
                    f"[ERROR] Duplicate group name detected under same parent: "
                    f'name="{name}", existing_group_id={existing_group_id}, '
                    f'incoming_group_id={incoming_group_id}. Skipping.'
                )
                return None

            # ✅ Same group_id → update attributes
            merged_attrs = dict(current_attrs)
            if attributes:
                for k, v in attributes.items():
                    merged_attrs[k] = v

            self.update_group(existing_id, {"name": name, "attributes": merged_attrs})
            return existing_id

        # No existing group → create new
        payload = {"name": name}
        if attributes:
            payload["attributes"] = attributes

        return self.create_group(payload, parent_id=parent_id)

    # --------- your existing path logic (kept, but uses helpers) ---------

    def check_keycloak_group_path(self, group_path):
        """
        Returns True if full path exists, else False.
        """
        return self.get_group_id_by_path(group_path) is not None

    def create_group_path(self, group_path):
        """
        Ensures group path exists, creates missing segments.
        Returns final group id.
        """
        parent_id = None
        for group in group_path:
            existing = self.find_child_by_name(parent_id, group)
            if existing:
                parent_id = existing
                continue

            parent_id = self.create_group({"name": group}, parent_id=parent_id)
        return parent_id