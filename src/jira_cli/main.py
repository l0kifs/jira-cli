"""Main CLI application"""

import typer
from rich.console import Console

from jira_cli.commands import auth, field, issue, project

app = typer.Typer(
    name="jira-cli",
    help="A lightweight CLI client for Jira Cloud REST API v3",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(auth.app, name="auth")
app.add_typer(field.app, name="field")
app.add_typer(issue.app, name="issue")
app.add_typer(project.app, name="project")

console = Console()


@app.command()
def version() -> None:
    """Show version information"""
    console.print("[bold]jira-cli[/bold] version [cyan]0.1.0[/cyan]")


def run():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    run()
