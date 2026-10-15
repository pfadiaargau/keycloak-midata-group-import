import requests
from requests.adapters import HTTPAdapter

REQUEST_TIMEOUT = 30


class MidataAPIService:
    def __init__(self, midata_url, midata_token, max_connections: int = 10):
        self.midata_url = midata_url
        self.midata_token = midata_token
        self.headers = {
            "X-Token": self.midata_token,
            "Content-Type": "application/json"
        }
        # Session hält Verbindungen offen; Pool gross genug für parallele Requests
        self.session = requests.Session()
        adapter = HTTPAdapter(pool_connections=max_connections, pool_maxsize=max_connections)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
    def get_group_info(self, group_id):
        try:
            response = self.session.get(
                f"{self.midata_url}/api/groups/{group_id}", headers=self.headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata group info for group ID {group_id}: {e}")
            return None
        
    def get_event_info(self, event_id, group_id):
        try:
            response = self.session.get(
                f"{self.midata_url}/api/events/{event_id}", headers=self.headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json().get("data")
            if not data:
                print(f"No event found for event ID {event_id} in group ID {group_id}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata event info for event ID {event_id}: {e}")
            return None
    
    def get_old_event_info(self, event_id, group_id):
        try:
            response = self.session.get(f"{self.midata_url}/de/groups/{group_id}/events/{event_id}.json",
                                        params={"token": self.midata_token}, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            events = response.json().get("events")
            if not events:
                print(f"No event found for event ID {event_id} in group ID {group_id}")
                return None
            return events[0]
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata event info for event ID {event_id}: {e}")
            return None
