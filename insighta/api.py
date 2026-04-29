import requests
from insighta.auth import load_credentials, save_credentials, BACKEND_URL, clear_credentials

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

    def _refresh_token(self):
        creds = load_credentials()
        try:
            resp = self.session.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": creds.get("refresh_token")}
            )
            resp.raise_for_status()
            data = resp.json()
            # Update credentials file with new tokens
            creds["access_token"] = data["access_token"]
            creds["refresh_token"] = data["refresh_token"]
            save_credentials(creds)
            return True
        except Exception:
            clear_credentials()
            raise Exception("Session expired. Please run 'insighta login' again.")

    def request(self, method, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_headers())
        
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, headers=headers, **kwargs)

        # Handle Transparent Token Refresh
        if response.status_code == 401:
            self._refresh_token()
            headers.update(self._get_auth_headers())
            response = self.session.request(method, url, headers=headers, **kwargs)

        return response