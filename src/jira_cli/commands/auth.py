"""Authentication and credential management commands"""
import typer
from rich.console import Console
from rich.prompt import Prompt

from jira_cli.config.credentials import CredentialStorage

app = typer.Typer(help="Authentication and credential management")
console = Console()


@app.command("login")
def login(
    domain: str = typer.Option(None, "--domain", "-d", help="Jira domain (e.g., your-domain.atlassian.net)"),
    email: str = typer.Option(None, "--email", "-e", help="Email associated with your Jira account"),
    api_token: str = typer.Option(None, "--api-token", "-t", help="API token for authentication"),
) -> None:
    """
    Store Jira credentials securely for future use.
    
    Credentials are stored in your system's secure credential store
    (macOS Keychain, Windows Credential Locker, or Linux Secret Service).
    
    If no options are provided, you will be prompted interactively.
    """
    try:
        # Prompt for missing values
        if not domain:
            domain = Prompt.ask("[cyan]Jira domain[/cyan] (e.g., your-domain.atlassian.net)")
        
        if not email:
            email = Prompt.ask("[cyan]Email[/cyan]")
        
        if not api_token:
            api_token = Prompt.ask("[cyan]API token[/cyan]", password=True)
        
        # Validate inputs
        if not domain or not email or not api_token:
            console.print("[red]Error: All credentials are required[/red]")
            raise typer.Exit(1)
        
        # Store credentials
        CredentialStorage.store_credentials(domain, email, api_token)
        
        console.print("✓ [green]Credentials stored successfully![/green]")
        console.print("\nYou can now use jira-cli commands without providing credentials.")
        console.print("\nTo update credentials, run: [cyan]jira-cli auth update[/cyan]")
        console.print("To logout, run: [cyan]jira-cli auth logout[/cyan]")
    except Exception as e:
        console.print(f"[red]Error storing credentials: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("update")
def update(
    domain: str = typer.Option(None, "--domain", "-d", help="New Jira domain"),
    email: str = typer.Option(None, "--email", "-e", help="New email"),
    api_token: str = typer.Option(None, "--api-token", "-t", help="New API token"),
) -> None:
    """
    Update stored credentials.
    
    You can update individual fields or all at once. Fields not provided
    will keep their current values.
    """
    try:
        # Get current credentials
        current_creds = CredentialStorage.get_credentials()
        
        if not current_creds:
            console.print("[yellow]No credentials found. Use 'jira-cli auth login' to store credentials first.[/yellow]")
            raise typer.Exit(1)
        
        current_domain, current_email, current_token = current_creds
        
        # Prompt for updates with current values as defaults
        if domain is None:
            domain = Prompt.ask(
                f"[cyan]Jira domain[/cyan] [dim](current: {current_domain})[/dim]",
                default=current_domain
            )
        
        if email is None:
            email = Prompt.ask(
                f"[cyan]Email[/cyan] [dim](current: {current_email})[/dim]",
                default=current_email
            )
        
        if api_token is None:
            update_token = Prompt.ask(
                "[cyan]Update API token?[/cyan]",
                choices=["yes", "no"],
                default="no"
            )
            if update_token == "yes":
                api_token = Prompt.ask("[cyan]New API token[/cyan]", password=True)
            else:
                api_token = current_token
        
        # Store updated credentials
        CredentialStorage.store_credentials(domain, email, api_token)
        
        console.print("✓ [green]Credentials updated successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error updating credentials: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("logout")
def logout(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """
    Delete stored credentials.
    
    This removes all stored credentials from your system's secure credential store.
    You will need to login again to use jira-cli commands.
    """
    try:
        if not CredentialStorage.has_credentials():
            console.print("[yellow]No credentials found to delete.[/yellow]")
            raise typer.Exit(0)
        
        if not force:
            confirm = Prompt.ask(
                "[yellow]Are you sure you want to delete your stored credentials?[/yellow]",
                choices=["yes", "no"],
                default="no"
            )
            if confirm != "yes":
                console.print("Cancelled.")
                raise typer.Exit(0)
        
        CredentialStorage.delete_credentials()
        console.print("✓ [green]Credentials deleted successfully![/green]")
        console.print("\nTo login again, run: [cyan]jira-cli auth login[/cyan]")
    except Exception as e:
        console.print(f"[red]Error deleting credentials: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("status")
def status() -> None:
    """
    Show authentication status.
    
    Displays whether credentials are stored and shows the domain and email
    (but not the API token for security reasons).
    """
    try:
        credentials = CredentialStorage.get_credentials()
        
        if credentials:
            domain, email, _ = credentials
            console.print("[green]✓ Authenticated[/green]\n")
            console.print(f"Domain: [cyan]{domain}[/cyan]")
            console.print(f"Email:  [cyan]{email}[/cyan]")
            console.print(f"Token:  [dim]••••••••[/dim] [dim](hidden for security)[/dim]")
            console.print("\nTo update credentials: [cyan]jira-cli auth update[/cyan]")
            console.print("To logout: [cyan]jira-cli auth logout[/cyan]")
        else:
            console.print("[yellow]Not authenticated[/yellow]\n")
            console.print("No stored credentials found.")
            console.print("\nTo login, run: [cyan]jira-cli auth login[/cyan]")
            console.print("\nAlternatively, you can use environment variables:")
            console.print("  JIRA_CLI__JIRA_DOMAIN")
            console.print("  JIRA_CLI__JIRA_EMAIL")
            console.print("  JIRA_CLI__JIRA_API_TOKEN")
    except Exception as e:
        console.print(f"[red]Error checking authentication status: {str(e)}[/red]")
        raise typer.Exit(1)
