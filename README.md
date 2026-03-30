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

   - `MIDATA_ROOT_GROUP_IDS`: A comma-separated list of MiData root group IDs to import. They need to be of the same type (e.g., `4691,1234`).
   - `KEYCLOAK_GROUP_ROOT`: The name of the root group in Keycloak under which the imported groups will be created. With this manual created lists can be separated (e.g., `midata`).
3. Run the import script:
    ```bash
        python3 import.py
    ```

## Configuration
In the script a few settings can be adjusted:
- `RECREATE_HIRARCHY`: If set to `True`, the script will refetch all the groups and events from MiData and import/update them in Keycloak. If set to `False`, the script will take the data fetched last time. If no data is available, it will fetch the data from MiData and import it into Keycloak.

- `EVENTS_TO_SYNC`: A list of events to sync. Each event is defined by a dictionary with the following keys:
  - `group_id`: The MiData group ID the event belongs to.
  - `event_id`: The MiData event ID.
  - `short_name`: A short name for the event, which will be used as the name of the corresponding group in Keycloak.

- `ROLE_GROUP_OVERRIDES`: A dictionary that allows to override the default group for a specific MiData role. The key is the MiData group id and the dictionary values can be `whitelist` and `blacklist`.
  - `whitelist`: A set of MiData roles that can be added in addition to the default roles defined in the `GroupDefinition` for the group. 
  - `blacklist`: A set of MiData roles that should be removed from the default roles defined in the `GroupDefinition` for the group.


- `GroupDefinition`: A dataclass that defines the structure of a group to be imported into Keycloak. Whether to create category groups (e.g., "Abteilung", "Gremien"). The group definitions are defined in the `GROUP_DEFINITIONS` dictionary in `model/GroupDefinitions.py`. Also which roles groups are created and which MiData roles are assigned to these groups. 

- `EventTypeDefinition`: A dataclass that defines the structure of an event type to be imported into Keycloak. The event type definitions are defined in the `EVENT_TYPE_DEFINITIONS` dictionary in `model/EventDefinitions.py`. The definition also creates subcategories for the events based on the roles. With this the leadership of a event and the participants can be separated. Those subcategories are fully customizable and can be defined for each event type separately. The roles that are assigned to the subcategories are also customizable.

## Project info
This project has been created by the IT team of the [Pfadi Aargau](https://www.pfadiaargau.ch/) to import the groups, roles and events from MiData into Keycloak. Main development was led by [Fynn Westerath v/o Raik](mailto:raik@pfadiaargau.ch).