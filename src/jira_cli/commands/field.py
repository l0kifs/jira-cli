"""Field-related CLI commands"""

from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="Field operations")


@app.command("search")
def search_fields(
    query: Optional[str] = typer.Option(
        None, "--query", "-q", help="Text to search in field name or description"
    ),
    field_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Field types to filter by (comma-separated, e.g., 'custom')",
    ),
    field_ids: Optional[str] = typer.Option(
        None, "--ids", help="Specific field IDs to include (comma-separated)"
    ),
    order_by: Optional[str] = typer.Option(
        None, "--order-by", help="Field to sort results by"
    ),
    expand: Optional[str] = typer.Option(
        None, "--expand", help="Fields to expand in the response"
    ),
    project_ids: Optional[str] = typer.Option(
        None, "--project-ids", help="Project IDs to filter by (comma-separated)"
    ),
    start_at: int = typer.Option(0, "--start-at", help="Index of first result"),
    max_results: int = typer.Option(
        50, "--max-results", help="Maximum number of results"
    ),
) -> None:
    """Returns a paginated list of fields for Classic Jira projects. The list can include all fields, specific fields, fields that contain a string in the field name or description, or specific fields that contain a string in the field name or description. Use type must be set to custom to show custom fields only."""
    try:
        field_type_list = field_type.split(",") if field_type else []
        field_ids_list = field_ids.split(",") if field_ids else []
        project_ids_list = (
            [int(pid.strip()) for pid in project_ids.split(",")] if project_ids else []
        )
        with get_client() as client:
            result = client.search_fields(
                query=query,
                field_type=field_type_list,
                field_ids=field_ids_list,
                order_by=order_by,
                expand=expand,
                project_ids=project_ids_list,
                start_at=start_at,
                max_results=max_results,
            )
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("list")
def list_fields() -> None:
    """Returns system and custom issue fields according to the following rules: Fields that cannot be added to the issue navigator are always returned. Fields that cannot be placed on an issue screen are always returned. Fields that depend on global Jira settings are only returned if the setting is enabled. That is, timetracking fields, subtasks, votes, and watches. For all other fields, this operation only returns the fields that the user has permission to view (that is, the field is used in at least one project that the user has Browse Projects project permission for.) This operation can be accessed anonymously."""
    try:
        with get_client() as client:
            result = client.get_fields()
        print_json(result)
    except Exception as e:
        handle_error(e)
