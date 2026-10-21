# keycloak-midata-group-import

This script imports groups, roles and events from MiData into Keycloak. It is designed to be run once to set up the initial structure in Keycloak, and can be re-run to update the structure if needed.

## Usage
1. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```
2. Set up environment variables (.env.example):
   - `KEYCLOAK_URL`: The URL of your Keycloak instance (e.g., `http://localhost:8080/auth`).
   - `KEYCLOAK_REALM`: The name of the Keycloak realm to import the structure into (e.g., `pbs`).
   - `KEYCLOAK_USER_REALM`: The realm to authenticate against (e.g., `master`).
   - `KEYCLOAK_USERNAME`: The username to use for authentication (e.g., `admin`, `import_script`).
   - `KEYCLOAK_PASSWORD`: The password to use for authentication (e.g., `admin`).

   - `MIDATA_URL`: The base URL of the MiData API (e.g., `https://db.scout.ch`). 
   - `MIDATA_SERVICE_ACCOUNT_TOKEN`: The token to authenticate with the MiData API.

3. Adjust `config.toml` (see [Configuration](#configuration)).
4. Run the import script:
    ```bash
        python3 import.py
    ```
   Options:
   - `--config <file>`: Use another config file (default: `config.toml`), e.g. one per deployment.
   - `--use-cache`: Use the hierarchy fetched last time (`detailed_hierarchy.json`, `categorized_groups.json`) instead of fetching it again from MiData. If no data is available, it is fetched from MiData.

## Configuration
Credentials and URLs live in `.env`, everything structural lives in `config.toml`. The file is validated at startup: unknown keys, unknown roles and duplicate event IDs abort the import with an error. Every option is documented in the file itself.

- `keycloak_group_root`: The name (or path) of the Keycloak group under which the imported groups are created (e.g. `midata`).
- `fetch_workers`: Number of parallel requests to MiData.

- `[[roots]]`: The MiData root groups to import, including all subgroups. They need to be of the same type.
  - `id`: The MiData group ID.
  - `only_subtrees`: Optional. Only import these groups (with their subgroups) and their parents up to the root.

- `[groups.<id>]`: Settings for a specific MiData group, on top of its `GroupDefinition`.
  - `role_subgroups`: `false` creates no role subgroups. The "Rollen" container still exists.
  - `roles_add`: Roles that get a subgroup in addition to the default roles of the `GroupDefinition`.
  - `roles_remove`: Default roles of the `GroupDefinition` that get no subgroup.
  - `collections`: `false` creates no collection groups.
  - `[[groups.<id>.extra_collections]]`: Additional collection groups (`key`, `label`, `roles`). A collection with the same `key` replaces the one from the `GroupDefinition`.

- `[events.<group_id>]`: The events to sync, in lists with any name (e.g. per year). Each event has:
  - `id`: The MiData event ID.
  - `short_name`: Optional. Name of the group in Keycloak. Defaults to the course number, otherwise the event name.
  - `comment`: Optional. Stored as the attribute `comment` in Keycloak.

The following is defined in code:

- `GroupDefinition`: A dataclass that defines the structure of a group to be imported into Keycloak. Whether to create category groups (e.g., "Abteilung", "Gremien"). The group definitions are defined in the `GROUP_DEFINITIONS` dictionary in `model/GroupDefinitions.py`. Also which roles groups are created and which MiData roles are assigned to these groups. 

- `EventTypeDefinition`: A dataclass that defines the structure of an event type to be imported into Keycloak. The event type definitions are defined in the `EVENT_TYPE_DEFINITIONS` dictionary in `model/EventDefinitions.py`. The definition also creates subcategories for the events based on the roles. With this the leadership of a event and the participants can be separated. Those subcategories are fully customizable and can be defined for each event type separately. The roles that are assigned to the subcategories are also customizable.

## Project info
This project has been created by the IT team of the [Pfadi Aargau](https://www.pfadiaargau.ch/) to import the groups, roles and events from MiData into Keycloak. Main development was led by [Fynn Westerath v/o Raik](mailto:raik@pfadiaargau.ch).