import requests


class MidataAPIService:
    def __init__(self, midata_url, midata_token):
        self.midata_url = midata_url
        self.midata_token = midata_token
        self.headers = {
            "X-Token": self.midata_token,
            "Content-Type": "application/json"
        }
        
    def get_group_info(self, group_id):
        try:
            response = requests.get(f"{self.midata_url}/api/groups/{group_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata group info for group ID {group_id}: {e}")
            return None
        
    def get_event_info(self, event_id, group_id):
        try:
            response = requests.get(f"{self.midata_url}/api/events/{event_id}", headers=self.headers)
            response.raise_for_status()
            if "data" not in response.json() or not response.json()["data"]:
                print(f"No event found for event ID {event_id} in group ID {group_id}")
                return None
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata event info for event ID {event_id}: {e}")
            return None
    
    def get_old_event_info(self, event_id, group_id):
        try:
            response = requests.get(f"{self.midata_url}/de/groups/{group_id}/events/{event_id}.json",
                                    params={"token": self.midata_token})
            response.raise_for_status()
            if "events" not in response.json() or not response.json()["events"]:
                print(f"No event found for event ID {event_id} in group ID {group_id}")
                return None
            return response.json()["events"][0]
        except requests.exceptions.RequestException as e:
            print(f"MS: Error fetching midata event info for event ID {event_id}: {e}")
            return None
