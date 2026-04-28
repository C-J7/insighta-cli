import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Configuration
CREDENTIALS_DIR = Path.home() / ".insighta"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

BACKEND_URL = os.getenv("PROFILEME_BACKEND_URL", "http://localhost:8000")