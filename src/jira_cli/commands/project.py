"""Project-related CLI commands"""

from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="Project operations")


@app.command("list")
def list_projects() -> None:
    """Get all projects visible to user"""
    try:
        with get_client() as client:
            result = client.get_projects()
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("create-meta")
def get_create_meta(
    project_key: str = typer.Argument(..., help="Project key"),
    issue_type_id: Optional[str] = typer.Option(
        None, "--issue-type", help="Issue type ID"
    ),
) -> None:
    """Get issue create metadata for a project"""
    try:
        with get_client() as client:
            result = client.get_create_metadata(
                project_key, issue_type_id=issue_type_id
            )
        print_json(result)
    except Exception as e:
        handle_error(e)
