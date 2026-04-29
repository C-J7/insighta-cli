import click
import requests
import os 
import webbrowser
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

@cli.command()
def login():
    """Authenticate via GitHub using PKCE."""
    state = os.urandom(16).hex()
    code_verifier, code_challenge = generate_pkce_pair()
    local_port = 8080
    redirect_uri = f"http://localhost:{local_port}/callback"

    # Get base GitHub URL from Backend
    try:
        resp = requests.get(f"{BACKEND_URL}/auth/github", params={"redirect_uri": redirect_uri})
        resp.raise_for_status()
        github_url = resp.json().get("url")
    except Exception as e:
        console.print(f"[red]Failed to contact backend: {e}[/red]")
        return

    # Append PKCE parameters
    pkce_params = {
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    auth_url = f"{github_url}&{urlencode(pkce_params)}"

    console.print("[cyan]Opening browser for GitHub authentication...[/cyan]")
    webbrowser.open(auth_url)

    # Start local server to catch the callback
    server = HTTPServer(('localhost', local_port), OAuthCallbackHandler)
    server.auth_code = None
    server.auth_state = None
    server.handle_request() # Wait for exactly one request

    if server.auth_state != state:
        console.print("[red]Authentication failed: State mismatch. Possible CSRF attack.[/red]")
        return

    if not server.auth_code:
        console.print("[red]Authentication failed: No code returned.[/red]")
        return
    
    # Exchange code for tokens at the Backend
    with console.status("[cyan]Exchanging code for tokens...[/cyan]"):
        try:
            exchange_resp = requests.get(
                f"{BACKEND_URL}/auth/github/callback",
                params={"code": server.auth_code, "code_verifier": code_verifier}
            )
            exchange_resp.raise_for_status()
            data = exchange_resp.json()
            save_credentials(data)
            console.print(f"[green]Successfully logged in as @{data.get('username')} ({data.get('role')})[/green]")
        except Exception as e:
            console.print(f"[red]Failed to exchange tokens: {e}[/red]")


@cli.command()
def logout():
    """Clear stored credentials."""
    try:
        api.request("POST", "/auth/logout")
    except Exception:
        pass # Ignore network errors on logout
    clear_credentials()
    console.print("[green]Logged out successfully.[/green]")

@cli.command()
def whoami():
    """Display current user info."""
    creds = load_credentials()
    if creds:
        console.print(f"[green]Logged in as @{creds.get('username')} (Role: {creds.get('role')})[/green]")
    else:
        console.print("[yellow]Not logged in.[/yellow]")


@cli.group()
def profiles():
    """Manage user profiles."""
    pass

# List profiles with filtering and pagination
@profiles.command()
@click.option('--gender', help='Filter by gender')
@click.option('--country', 'country_id', help='Filter by country ISO code')
@click.option('--age-group', help='Filter by age group')
@click.option('--min-age', type=int, help='Minimum age')
@click.option('--max-age', type=int, help='Maximum age')
@click.option('--sort-by', default='created_at', help='Sort column')
@click.option('--order', default='desc', help='Sort order (asc/desc)')
@click.option('--page', default=1, type=int, help='Page number')
@click.option('--limit', default=10, type=int, help='Results per page')

def list(gender, country_id, age_group, min_age, max_age, sort_by, order, page, limit):
    """List profiles with filtering and pagination."""
    params = {k: v for k, v in locals().items() if v is not None}
    
    with console.status("[cyan]Fetching profiles...[/cyan]"):
        try:
            resp = api.request("GET", "/api/profiles", params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            console.print(f"[red]API Error: {e}[/red]")
            return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Country")

    for p in data.get("data", []):
        table.add_row(p["id"][:8]+"...", p["name"].title(), p["gender"], str(p["age"]), p["country_id"])

    console.print(table)
    console.print(f"[dim]Page {data.get('page')} of {data.get('total_pages')} (Total: {data.get('total')})[/dim]")

@profiles.command()
@click.argument('query')
def search(query):
    """Search profiles using a Natural Language Query."""
    params = {"search": query}
    
    with console.status("[cyan]Searching profiles...[/cyan]"):
        try:
            resp = api.request("GET", "/api/profiles/search", params={"q": query})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            console.print(f"[red]Search Failed: {e}[/red]")
            return
            
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Name"); table.add_column("Gender"); table.add_column("Age"); table.add_column("Country")
    for p in data.get("data", []):
        table.add_row(p["name"].title(), p["gender"], str(p["age"]), p["country_id"])
    console.print(table)