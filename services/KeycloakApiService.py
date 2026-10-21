import requests


class KeycloakApiService:
    def __init__(self, keycloak_url, keycloak_realm, keycloak_user_realm, keycloak_username, keycloak_password):
        self.keycloak_url = keycloak_url.rstrip("/")
        self.keycloak_realm = keycloak_realm
        self.keycloak_user_realm = keycloak_user_realm
        self.keycloak_username = keycloak_username
        self.keycloak_password = keycloak_password
        # One session for all requests: keeps the connection open (no new TCP/TLS handshake per request)
        self.session = requests.Session()
        # parent_id -> {name: group representation}; loaded once per parent
        self._children_cache: dict[str, dict[str, dict]] = {}
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
            response = self.session.post(token_url, data=data, timeout=30)
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

    def _request(self, method: str, url: str, *, json_body: dict | None = None, **kwargs):
        """Make an authenticated request, refreshing the token once after a 401."""
        headers = self._headers(json=json_body is not None)
        response = self.session.request(
            method,
            url,
            headers=headers,
            json=json_body,
            **kwargs,
        )

        if response.status_code == 401:
            self.token = self.get_token()
            response = self.session.request(
                method,
                url,
                headers=self._headers(json=json_body is not None),
                json=json_body,
                **kwargs,
            )

        return response

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

        r = self._request(
            "GET",
            f"{self._admin_base()}/groups",
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_group(self, group_id: str) -> dict:
        r = self._request(
            "GET",
            f"{self._admin_base()}/groups/{group_id}",
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_group_children(self, group_id: str, page_size: int = 500) -> list:
        """Loads all direct children including attributes (paginated)."""
        children: list = []
        first = 0
        while True:
            r = self._request(
                "GET",
                f"{self._admin_base()}/groups/{group_id}/children",
                params={"first": first, "max": page_size, "briefRepresentation": "false"},
                timeout=30,
            )
            r.raise_for_status()
            page = r.json()
            children.extend(page)
            if len(page) < page_size:
                return children
            first += page_size

    def _get_children_map(self, parent_id: str, refresh: bool = False) -> dict[str, dict]:
        if refresh or parent_id not in self._children_cache:
            self._children_cache[parent_id] = {
                g.get("name"): g for g in self.get_group_children(parent_id)
            }
        return self._children_cache[parent_id]

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

        r = self._request(
            "POST",
            url,
            json_body=payload,
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
        r = self._request(
            "PUT",
            f"{self._admin_base()}/groups/{group_id}",
            json_body=payload,
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

        child = self._get_children_map(parent_id).get(name)
        return child.get("id") if child else None

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

    def _find_child(self, parent_id: str | None, name: str, refresh: bool = False) -> dict | None:
        """Returns the representation of a direct child (including attributes) or None."""
        if parent_id is None:
            gid = self.find_child_by_name(None, name)
            return self.get_group(gid) if gid else None

        child = self._get_children_map(parent_id, refresh=refresh).get(name)
        if child is not None and "attributes" not in child:
            # Older Keycloak versions may not return attributes in the children list
            child = self.get_group(child["id"])
            self._children_cache[parent_id][name] = child
        return child

    def _update_existing(
        self,
        parent_id: str | None,
        current: dict,
        name: str,
        attributes: dict | None,
        remove_attributes: set[str] | None,
        incoming_group_id: str | None,
        context: str,
    ) -> str | None:
        current_attrs = current.get("attributes") or {}
        existing_group_id = self._extract_first_attr(current_attrs, "group_id")

        # Real name conflict between two actual MIDATA groups
        if existing_group_id and incoming_group_id and existing_group_id != incoming_group_id:
            print(
                f"[ERROR] Duplicate group name detected {context}: "
                f'name="{name}", existing_group_id={existing_group_id}, '
                f'incoming_group_id={incoming_group_id}. Skipping.'
            )
            return None

        merged_attrs = dict(current_attrs)
        if attributes:
            merged_attrs.update(attributes)
        for k in remove_attributes or ():
            merged_attrs.pop(k, None)

        # Only write if something actually changed
        if merged_attrs != current_attrs:
            self.update_group(current["id"], {"name": name, "attributes": merged_attrs})
            current["attributes"] = merged_attrs

        return current["id"]

    def upsert_group(
        self,
        parent_id: str | None,
        name: str,
        attributes: dict | None = None,
        remove_attributes: set[str] | None = None,
    ) -> str | None:
        """
        Create group if missing.

        remove_attributes: attribute keys to drop from an existing group (e.g. obsolete attributes).

        If group with same name exists under same parent:
            - If same group_id attribute -> update (only if attributes changed)
            - If different group_id attribute -> skip and return None

        If a create hits 409, re-check the parent for an existing child with the same name
        and continue with that group. This makes the method idempotent.
        """
        incoming_group_id = self._extract_first_attr(attributes, "group_id")

        current = self._find_child(parent_id, name)
        if current:
            return self._update_existing(
                parent_id, current, name, attributes, remove_attributes,
                incoming_group_id, "under same parent",
            )

        payload = {"name": name}
        if attributes:
            payload["attributes"] = attributes

        created_id = self.create_group(payload, parent_id=parent_id)

        # Successfully created
        if created_id:
            if parent_id is not None:
                self._children_cache[parent_id][name] = {
                    "id": created_id,
                    "name": name,
                    "attributes": dict(attributes or {}),
                }
            return created_id

        # 409: cache is stale -> reload children and look again
        current = self._find_child(parent_id, name, refresh=True)
        if not current:
            raise RuntimeError(
                f"Keycloak returned 409 while creating group '{name}', "
                f"but the group could not be found afterwards under parent '{parent_id}'."
            )

        return self._update_existing(
            parent_id, current, name, attributes, remove_attributes,
            incoming_group_id, "after 409 conflict",
        )

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
            if parent_id is not None:
                # The children list is now stale
                self._children_cache.pop(parent_id, None)
            if created is None:
                # On 409: resolve again
                created = self.find_child_by_name(parent_id, group)
                if not created:
                    raise RuntimeError(
                        f"Could not create or resolve path segment '{group}' under parent '{parent_id}'."
                    )
            parent_id = created
        return parent_id
