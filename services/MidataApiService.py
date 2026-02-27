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
            print(f"Error fetching midata group info for group ID {group_id}: {e}")
            return None
    
    