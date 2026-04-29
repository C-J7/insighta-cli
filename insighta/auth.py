import os
import json
import base64
import hashlib
import webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Configuration
CREDENTIALS_DIR = Path.home() / ".insighta"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Catches the GitHub redirect callback locally."""
    def do_GET(self):
        if self.path.startswith('/favicon.ico'):
            self.send_response(204)
            self.end_headers()
            return

        query_components = parse_qs(urlparse(self.path).query)
        self.server.auth_code = query_components.get('code', [None])[0]
        self.server.auth_state = query_components.get('state', [None])[0]
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <html><body>
        <h1 style='color: #2f5c79; font-family: sans-serif; text-align: center; margin-top: 20%;'>
            Authentication Successful! You can close this window and return to your terminal.
        </h1>
        <script>
            // Attempt to automatically close the tab for a smoother UX
            setTimeout(() => window.close(), 1000);
        </script>
        </body></html>
        """
        self.wfile.write(html.encode('utf-8'))

def generate_pkce_pair():
    """Generates a code_verifier and code_challenge for PKCE."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8').rstrip('=')
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def save_credentials(data):
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f)

def load_credentials():
    if not CREDENTIALS_FILE.exists():
        return None
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def clear_credentials():
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()