from datetime import datetime, timedelta
import requests

OURA_AUTH_URL="https://cloud.ouraring.com/oauth/authorize"
OURA_ACCESS_TOKEN_URL="https://api.ouraring.com/oauth/token"
OURA_API_URL="https://api.ouraring.com/v2"

class OuraClientBase:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

    def get_token(self):
        raise NotImplementedError("Subclasses must implement get_token method")

    def authenticate(self):
        raise NotImplementedError("Subclasses must implement authenticate method")



    def get_heart_rate(self, start_date: str, end_date: str):
        url = f"{OURA_API_URL}/usercollection/heartrate"
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch heart rate data: {response.status_code} - {response.text}")


class OuraClientPersonal(OuraClientBase):
    def __init__(self, personal_token):
        super().__init__()
        self.personal_token = personal_token

    def get_token(self):
        return self.personal_token

    def authenticate(self):
        # No authentication needed for personal token
        pass


class OuraClientOAuth(OuraClientBase):
    def __init__(self, client_id, client_secret):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        if not self.access_token or datetime.now() >= self.expires_at:
            self.authenticate()
        return self.access_token

    def authenticate(self):
        # Implement OAuth authentication logic here
        # This should set self.access_token, self.refresh_token, and self.expires_at
        pass
