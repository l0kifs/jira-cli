"""Utility functions for CLI commands"""
import json
import sys
from typing import Any

from rich.console import Console
from rich.json import JSON

from jira_cli.api.client import JiraClient
from jira_cli.config.credentials import CredentialStorage
from jira_cli.config.settings import get_settings

console = Console()


def get_client() -> JiraClient:
    """
    Get configured Jira client instance.
    
    First tries to use stored credentials from the system keyring,
    then falls back to environment variables.
    
    Returns:
        JiraClient instance
        
    Raises:
        SystemExit if configuration is missing
    """
    # Try to get credentials from keyring first
    stored_creds = CredentialStorage.get_credentials()
    
    if stored_creds:
        domain, email, api_token = stored_creds
        return JiraClient(domain, email, api_token)
    
    # Fall back to environment variables
    settings = get_settings()
    
    if not settings.jira_domain or not settings.jira_email or not settings.jira_api_token:
        console.print("[red]Error: Jira configuration missing![/red]")
        console.print("\n[yellow]Option 1: Store credentials securely[/yellow]")
        console.print("  Run: [cyan]jira-cli auth login[/cyan]")
        console.print("\n[yellow]Option 2: Use environment variables[/yellow]")
        console.print("  Set the following environment variables:")
        console.print("    JIRA_CLI__JIRA_DOMAIN")
        console.print("    JIRA_CLI__JIRA_EMAIL")
        console.print("    JIRA_CLI__JIRA_API_TOKEN")
        console.print("\n  Or create a .env file with these settings.")
        sys.exit(1)
    
    return JiraClient(settings.jira_domain, settings.jira_email, settings.jira_api_token)


def print_json(data: Any, pretty: bool = True) -> None:
    """
    Print data as JSON.
    
    Args:
        data: Data to print
        pretty: Whether to use Rich formatting
    """
    if pretty:
        json_str = json.dumps(data, indent=2)
        console.print(JSON(json_str))
    else:
        print(json.dumps(data))


def handle_error(e: Exception) -> None:
    """
    Handle and display error messages.
    
    Args:
        e: Exception to handle
    """
    console.print(f"[red]Error: {str(e)}[/red]")
    sys.exit(1)
