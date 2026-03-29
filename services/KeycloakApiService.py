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
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error fetching Keycloak token: {e}") from e

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
            out[k] = [str(v)] if not isinstance(v, list) else [str(x) for x in v]
        return out

    # --------- basic group CRUD ---------

    def get_groups(self, search: str | None = None) -> list:
        params = {}
        if search:
            params["search"] = search

        r = requests.get(
            f"{self._admin_base()}/groups",
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_group(self, group_id: str) -> dict:
        r = requests.get(
            f"{self._admin_base()}/groups/{group_id}",
            headers=self._headers(),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_group_children(self, group_id: str) -> list:
        r = requests.get(
            f"{self._admin_base()}/groups/{group_id}/children",
            params={"max": 100},
            headers=self._headers(),
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def create_group(self, payload: dict, parent_id: str | None = None) -> str | None:
        """
        Creates a group. If parent_id is None => top-level group.
        Returns created group id from Location header.
        Returns None on HTTP 409 conflict so caller can recover.
        """
        if parent_id is None:
            url = f"{self._admin_base()}/groups"
        else:
            url = f"{self._admin_base()}/groups/{parent_id}/children"

        r = requests.post(
            url,
            headers=self._headers(json=True),
            json=payload,
            timeout=30,
        )

        if r.status_code == 409:
            return None

        r.raise_for_status()

        loc = r.headers.get("Location", "")
        created_id = loc.rstrip("/").split("/")[-1]
        if not created_id:
            raise RuntimeError(
                f"Could not determine created Keycloak group id for payload name={payload.get('name')!r} "
                f"(missing Location header)."
            )
        return created_id

    def update_group(self, group_id: str, payload: dict) -> None:
        r = requests.put(
            f"{self._admin_base()}/groups/{group_id}",
            headers=self._headers(json=True),
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

    # --------- lookup helpers ---------

    def find_child_by_name(self, parent_id: str | None, name: str) -> str | None:
        """
        Finds a direct child group by exact name.
        If parent_id is None, searches top-level groups.
        """
        if parent_id is None:
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
        parent_id = None
        for part in group_path:
            gid = self.find_child_by_name(parent_id, part)
            if not gid:
                return None
            parent_id = gid
        return parent_id

    # --------- internal helpers ---------

    @staticmethod
    def _extract_first_attr(attributes: dict | None, key: str) -> str | None:
        if not attributes:
            return None
        values = attributes.get(key)
        if not values:
            return None
        if isinstance(values, list) and values:
            return str(values[0])
        return str(values)

    # --------- upsert helper ---------

    def upsert_group(self, parent_id: str | None, name: str, attributes: dict | None = None) -> str | None:
        """
        Create group if missing.

        If group with same name exists under same parent:
            - If same group_id attribute -> update normally
            - If different group_id attribute -> skip and return None

        If a create hits 409, re-check the parent for an existing child with the same name
        and continue with that group. This makes the method idempotent.
        """
        existing_id = self.find_child_by_name(parent_id, name)

        incoming_group_id = self._extract_first_attr(attributes, "group_id")

        if existing_id:
            current = self.get_group(existing_id)
            current_attrs = current.get("attributes") or {}
            existing_group_id = self._extract_first_attr(current_attrs, "group_id")

            # echter Namenskonflikt zwischen zwei realen MIDATA-Gruppen
            if existing_group_id and incoming_group_id and existing_group_id != incoming_group_id:
                print(
                    f"[ERROR] Duplicate group name detected under same parent: "
                    f'name="{name}", existing_group_id={existing_group_id}, '
                    f'incoming_group_id={incoming_group_id}. Skipping.'
                )
                return None

            merged_attrs = dict(current_attrs)
            if attributes:
                for k, v in attributes.items():
                    merged_attrs[k] = v

            self.update_group(existing_id, {"name": name, "attributes": merged_attrs})
            return existing_id

        payload = {"name": name}
        if attributes:
            payload["attributes"] = attributes

        created_id = self.create_group(payload, parent_id=parent_id)

        # Erfolgreich neu erstellt
        if created_id:
            return created_id

        # 409: jetzt nochmal nachschauen
        existing_id_after_conflict = self.find_child_by_name(parent_id, name)
        if not existing_id_after_conflict:
            raise RuntimeError(
                f"Keycloak returned 409 while creating group '{name}', "
                f"but the group could not be found afterwards under parent '{parent_id}'."
            )

        current = self.get_group(existing_id_after_conflict)
        current_attrs = current.get("attributes") or {}
        existing_group_id = self._extract_first_attr(current_attrs, "group_id")

        # wenn nach 409 eine andere MIDATA-Gruppe mit gleichem Namen gefunden wurde -> skip
        if existing_group_id and incoming_group_id and existing_group_id != incoming_group_id:
            print(
                f"[ERROR] Duplicate group name detected after 409 conflict: "
                f'name="{name}", existing_group_id={existing_group_id}, '
                f'incoming_group_id={incoming_group_id}. Skipping.'
            )
            return None

        merged_attrs = dict(current_attrs)
        if attributes:
            for k, v in attributes.items():
                merged_attrs[k] = v

        self.update_group(existing_id_after_conflict, {"name": name, "attributes": merged_attrs})
        return existing_id_after_conflict

    def check_keycloak_group_path(self, group_path):
        return self.get_group_id_by_path(group_path) is not None

    def create_group_path(self, group_path):
        parent_id = None
        for group in group_path:
            existing = self.find_child_by_name(parent_id, group)
            if existing:
                parent_id = existing
                continue

            created = self.create_group({"name": group}, parent_id=parent_id)
            if created is None:
                # Falls 409: nochmal auflösen
                created = self.find_child_by_name(parent_id, group)
                if not created:
                    raise RuntimeError(
                        f"Could not create or resolve path segment '{group}' under parent '{parent_id}'."
                    )
            parent_id = created
        return parent_id