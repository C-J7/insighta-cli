import click
from urllib.parse import urlencode
from http.server import HTTPServer
from rich.console import Console
from rich.table import Table

from insighta.auth import (
    generate_pkce_pair, OAuthCallbackHandler, save_credentials, 
    load_credentials, clear_credentials, BACKEND_URL
)
from insighta.api import InsightaAPI

console = Console()

api = InsightaAPI()

@click.group()
def cli():
    """Insighta Labs+ CLI """
    pass