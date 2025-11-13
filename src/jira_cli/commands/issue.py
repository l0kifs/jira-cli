"""Issue-related CLI commands"""
import json
from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="Issue operations")


@app.command("create")
def create_issue(
    fields: str = typer.Option(..., "--fields", "-f", help="JSON string with issue fields"),
) -> None:
    """Create a new issue. Fields should be JSON like: '{"project":{"key":"PROJ"},"summary":"Title","issuetype":{"name":"Bug"}}'"""
    try:
        fields_dict = json.loads(fields)
        with get_client() as client:
            result = client.create_issue(fields_dict)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("get")
def get_issue(
    issue_key: str = typer.Argument(..., help="Issue ID or key (e.g., PROJ-123)"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated list of fields to return"),
    expand: Optional[str] = typer.Option(None, "--expand", help="Comma-separated list of parameters to expand"),
) -> None:
    """Get issue details"""
    try:
        with get_client() as client:
            result = client.get_issue(issue_key, fields=fields, expand=expand)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("update")
def update_issue(
    issue_key: str = typer.Argument(..., help="Issue ID or key"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="JSON string with fields to update"),
    update: Optional[str] = typer.Option(None, "--update", "-u", help="JSON string with update operations"),
) -> None:
    """Update an issue. Use --fields for simple updates or --update for complex operations"""
    try:
        fields_dict = json.loads(fields) if fields else None
        update_dict = json.loads(update) if update else None
        
        if not fields_dict and not update_dict:
            typer.echo("Error: Either --fields or --update must be provided")
            raise typer.Exit(1)
        
        with get_client() as client:
            result = client.update_issue(issue_key, fields=fields_dict, update=update_dict)
        
        if result:
            print_json(result)
        else:
            typer.echo("Issue updated successfully")
    except Exception as e:
        handle_error(e)


@app.command("search")
def search_issues(
    jql: str = typer.Argument(..., help="JQL query string"),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated list of fields to return"),
    start_at: int = typer.Option(0, "--start-at", help="Index of first result"),
    max_results: int = typer.Option(50, "--max-results", help="Maximum number of results"),
) -> None:
    """Search for issues using JQL"""
    try:
        with get_client() as client:
            result = client.search_issues(jql, fields=fields, start_at=start_at, max_results=max_results)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("transitions")
def get_transitions(
    issue_key: str = typer.Argument(..., help="Issue ID or key"),
) -> None:
    """Get available transitions for an issue"""
    try:
        with get_client() as client:
            result = client.get_transitions(issue_key)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("transition")
def transition_issue(
    issue_key: str = typer.Argument(..., help="Issue ID or key"),
    transition_id: str = typer.Argument(..., help="Transition ID to perform"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="JSON string with fields to update"),
) -> None:
    """Transition an issue to a new status"""
    try:
        fields_dict = json.loads(fields) if fields else None
        
        with get_client() as client:
            result = client.transition_issue(issue_key, transition_id, fields=fields_dict)
        
        if result:
            print_json(result)
        else:
            typer.echo("Issue transitioned successfully")
    except Exception as e:
        handle_error(e)


@app.command("comments")
def get_comments(
    issue_key: str = typer.Argument(..., help="Issue ID or key"),
) -> None:
    """Get comments for an issue"""
    try:
        with get_client() as client:
            result = client.get_comments(issue_key)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("changelog")
def get_changelog(
    issue_key: str = typer.Argument(..., help="Issue ID or key"),
    start_at: int = typer.Option(0, "--start-at", help="Index of first result"),
    max_results: int = typer.Option(100, "--max-results", help="Maximum number of results"),
) -> None:
    """Get changelog/history for an issue"""
    try:
        with get_client() as client:
            result = client.get_changelog(issue_key, start_at=start_at, max_results=max_results)
        print_json(result)
    except Exception as e:
        handle_error(e)
