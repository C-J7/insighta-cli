import requests
from insighta.auth import load_credentials, BACKEND_URL

class InsightaAPI:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.headers.update({"X-API-Version": "1"})

    def _get_auth_headers(self):
        creds = load_credentials()
        if not creds or "access_token" not in creds:
            raise Exception("Not logged in. Run 'insighta login' first.")
        return {"Authorization": f"Bearer {creds['access_token']}"}