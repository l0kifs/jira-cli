"""Utility functions for CLI commands"""
import json
import sys
from typing import Any

from rich.console import Console
from rich.json import JSON

from jira_cli.api.client import JiraClient
from jira_cli.config.settings import get_settings

console = Console()


def get_client() -> JiraClient:
    """
    Get configured Jira client instance.
    
    Returns:
        JiraClient instance
        
    Raises:
        SystemExit if configuration is missing
    """
    settings = get_settings()
    
    if not settings.jira_domain or not settings.jira_email or not settings.jira_api_token:
        console.print("[red]Error: Jira configuration missing![/red]")
        console.print("\nPlease set the following environment variables:")
        console.print("  JIRA_CLI__JIRA_DOMAIN")
        console.print("  JIRA_CLI__JIRA_EMAIL")
        console.print("  JIRA_CLI__JIRA_API_TOKEN")
        console.print("\nOr create a .env file with these settings.")
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
