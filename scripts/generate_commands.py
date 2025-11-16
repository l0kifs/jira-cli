#!/usr/bin/env python3
"""
OpenAPI CLI Command Generator

This script generates CLI commands from Jira's OpenAPI v3 specification.
Users can select which REST API methods to convert to CLI commands.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

console = Console()
app = typer.Typer(help="Generate CLI commands from OpenAPI specification")


class OpenAPIParser:
    """Parse OpenAPI specification and extract command information"""

    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        with open(spec_path, "r") as f:
            self.spec = json.load(f)
        self.paths = self.spec.get("paths", {})

    def get_all_operations(self) -> List[Dict[str, Any]]:
        """Extract all operations from the OpenAPI spec"""
        operations = []
        for path, methods in self.paths.items():
            for method, details in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    operation = {
                        "path": path,
                        "method": method.upper(),
                        "operationId": details.get("operationId", ""),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "tags": details.get("tags", []),
                        "parameters": details.get("parameters", []),
                        "requestBody": details.get("requestBody"),
                        "deprecated": details.get("deprecated", False),
                    }
                    operations.append(operation)
        return operations

    def group_operations_by_tag(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group operations by their tags"""
        operations = self.get_all_operations()
        grouped = {}
        for op in operations:
            tags = op["tags"] if op["tags"] else ["Untagged"]
            for tag in tags:
                if tag not in grouped:
                    grouped[tag] = []
                grouped[tag].append(op)
        return grouped


class CommandGenerator:
    """Generate CLI command code from OpenAPI operations"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.commands_path = base_path / "src" / "jira_cli" / "commands"

    def sanitize_name(self, name: str) -> str:
        """Convert a name to a valid Python identifier"""
        # Convert to snake_case
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        # Remove invalid characters
        name = re.sub(r"[^a-z0-9_]", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = f"_{name}"
        return name

    def extract_path_params(self, path: str) -> List[str]:
        """Extract path parameter names from a path"""
        return re.findall(r"\{([^}]+)\}", path)

    def generate_function_name(self, operation: Dict[str, Any]) -> str:
        """Generate a function name from operation"""
        operation_id = operation.get("operationId", "")
        if operation_id:
            return self.sanitize_name(operation_id)

        # Fallback: use method and path
        method = operation["method"].lower()
        path = operation["path"].split("/")[-1]
        path = re.sub(r"\{([^}]+)\}", "", path)
        return f"{method}_{self.sanitize_name(path)}"

    def generate_command_name(self, operation: Dict[str, Any]) -> str:
        """Generate CLI command name from operation"""
        func_name = self.generate_function_name(operation)
        # Remove common prefixes
        for prefix in ["get_", "create_", "update_", "delete_", "list_"]:
            if func_name.startswith(prefix):
                return func_name
        return func_name

    def escape_string(self, text: str) -> str:
        """Escape special characters in strings for Python code"""
        # Replace quotes and newlines
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        text = text.replace("\n", " ")
        # Truncate long descriptions
        if len(text) > 200:
            text = text[:197] + "..."
        return text

    def generate_parameter_definition(
        self, param: Dict[str, Any], path_params: Set[str]
    ) -> Tuple[str, str, str]:
        """
        Generate parameter definition for a Typer command.
        Returns: (param_name, param_type, param_definition)
        """
        param_name = param["name"]
        param_in = param["in"]
        description = self.escape_string(param.get("description", ""))
        required = param.get("required", False)
        param_schema = param.get("schema", {})
        param_type = param_schema.get("type", "string")

        # Map OpenAPI types to Python types
        type_map = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "array": "str",  # Simplified: handle as comma-separated string
        }
        python_type = type_map.get(param_type, "str")

        # Generate parameter name (convert to snake_case)
        py_param_name = self.sanitize_name(param_name)

        if param_in == "path":
            # Path parameters are required arguments
            param_def = f'typer.Argument(..., help="{description}")'
            type_hint = python_type
        elif param_in == "query":
            # Query parameters are options
            if required:
                param_def = (
                    f'typer.Option(..., "--{param_name}", help="{description}")'
                )
                type_hint = python_type
            else:
                param_def = (
                    f'typer.Option(None, "--{param_name}", help="{description}")'
                )
                type_hint = f"Optional[{python_type}]"
        else:
            # Header or other parameters
            param_def = (
                f'typer.Option(None, "--{param_name}", help="{description}")'
            )
            type_hint = f"Optional[{python_type}]"

        return py_param_name, type_hint, param_def

    def generate_client_method_call(self, operation: Dict[str, Any]) -> str:
        """Generate the API client method call"""
        method = operation["method"].lower()
        path = operation["path"]

        # Extract path parameters
        path_params = self.extract_path_params(path)

        # Build the endpoint string
        endpoint = path
        for param in path_params:
            py_param = self.sanitize_name(param)
            endpoint = endpoint.replace(f"{{{param}}}", f"{{{py_param}}}")

        # Build the method call - use f-string only if there are path params
        if path_params:
            call_parts = [f'method="{method.upper()}"', f'endpoint=f"{endpoint}"']
        else:
            call_parts = [f'method="{method.upper()}"', f'endpoint="{endpoint}"']

        # Add params dict if there are query parameters
        query_params = [
            p for p in operation.get("parameters", []) if p.get("in") == "query"
        ]
        if query_params:
            params_dict = ", ".join(
                [
                    f'"{p["name"]}": {self.sanitize_name(p["name"])}'
                    for p in query_params
                ]
            )
            call_parts.append(f"params={{{params_dict}}}")

        # Add json body if there's a request body
        if operation.get("requestBody"):
            call_parts.append("json=json.loads(body) if body else None")

        return f"client._request({', '.join(call_parts)})"

    def generate_command_code(self, operation: Dict[str, Any]) -> str:
        """Generate complete command function code"""
        func_name = self.generate_function_name(operation)
        cmd_name = self.generate_command_name(operation)
        description = operation.get("description", operation.get("summary", ""))

        # Escape and truncate description for docstring
        description = self.escape_string(description)
        if len(description) > 500:
            description = description[:497] + "..."

        path_param_names = set(self.extract_path_params(operation["path"]))

        # Generate parameters
        params_def = []

        # Add path parameters first (as arguments)
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                py_name, py_type, param_def = self.generate_parameter_definition(
                    param, path_param_names
                )
                params_def.append(f"    {py_name}: {py_type} = {param_def},")

        # Add query parameters (as options)
        for param in operation.get("parameters", []):
            if param.get("in") == "query":
                py_name, py_type, param_def = self.generate_parameter_definition(
                    param, path_param_names
                )
                params_def.append(f"    {py_name}: {py_type} = {param_def},")

        # Add request body if present
        if operation.get("requestBody"):
            params_def.append(
                '    body: Optional[str] = typer.Option(None, "--body", "-b", help="JSON request body"),'
            )

        params_str = "\n".join(params_def)

        # Generate client call
        client_call = self.generate_client_method_call(operation)

        # Build the complete function
        code = f'''
@app.command("{cmd_name}")
def {func_name}(
{params_str}
) -> None:
    """{description}"""
    try:
        with get_client() as client:
            result = {client_call}
        print_json(result)
    except Exception as e:
        handle_error(e)
'''

        return code

    def generate_command_group(
        self, tag: str, operations: List[Dict[str, Any]]
    ) -> str:
        """Generate a complete command group file"""
        # Check what imports are needed
        needs_json = any(op.get("requestBody") for op in operations)
        needs_optional = any(
            p.get("required") is False
            for op in operations
            for p in op.get("parameters", [])
        ) or needs_json  # body parameter is always optional

        # Build imports dynamically
        imports = f'"""CLI commands for {tag}"""\n\n'

        if needs_json:
            imports += "import json\n"

        if needs_optional:
            imports += "from typing import Optional\n"

        imports += """
import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="{tag} operations")
""".format(tag=tag)

        # Generate all command functions
        commands = []
        for operation in operations:
            if not operation.get("deprecated"):
                commands.append(self.generate_command_code(operation))

        return imports + "\n".join(commands)

    def save_command_group(self, tag: str, code: str) -> Path:
        """Save generated command group to file"""
        tag_lower = self.sanitize_name(tag)
        file_path = self.commands_path / f"generated_{tag_lower}.py"

        with open(file_path, "w") as f:
            f.write(code)

        console.print(f"[green]✓[/green] Generated: {file_path}")
        return file_path


def display_operations_tree(grouped_operations: Dict[str, List[Dict[str, Any]]]):
    """Display operations in a tree structure"""
    tree = Tree("[bold]Available API Operations[/bold]")

    for tag, operations in sorted(grouped_operations.items()):
        tag_node = tree.add(f"[cyan]{tag}[/cyan] ({len(operations)} operations)")
        for op in operations[:5]:  # Show first 5 operations per tag
            summary = op["summary"] or op["operationId"]
            method_color = {
                "GET": "green",
                "POST": "blue",
                "PUT": "yellow",
                "DELETE": "red",
                "PATCH": "magenta",
            }.get(op["method"], "white")
            tag_node.add(
                f"[{method_color}]{op['method']}[/{method_color}] {summary}"
            )
        if len(operations) > 5:
            tag_node.add(f"[dim]... and {len(operations) - 5} more[/dim]")

    console.print(tree)


def display_operations_table(operations: List[Dict[str, Any]]):
    """Display operations in a table"""
    table = Table(title="Selected Operations", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Method", style="bold")
    table.add_column("Path", style="green")
    table.add_column("Operation ID", style="yellow")
    table.add_column("Summary")

    for idx, op in enumerate(operations, 1):
        method_color = {
            "GET": "green",
            "POST": "blue",
            "PUT": "yellow",
            "DELETE": "red",
            "PATCH": "magenta",
        }.get(op["method"], "white")
        table.add_row(
            str(idx),
            f"[{method_color}]{op['method']}[/{method_color}]",
            op["path"],
            op["operationId"],
            op["summary"][:50] + "..." if len(op["summary"]) > 50 else op["summary"],
        )

    console.print(table)


@app.command("list")
def list_operations(
    spec_path: Path = typer.Option(
        "docs/jira-openapi-v3.json",
        "--spec",
        "-s",
        help="Path to OpenAPI specification file",
    ),
    tag: Optional[str] = typer.Option(
        None, "--tag", "-t", help="Filter by tag/category"
    ),
):
    """List all available operations from the OpenAPI spec"""
    try:
        parser = OpenAPIParser(spec_path)
        grouped = parser.group_operations_by_tag()

        if tag:
            if tag in grouped:
                operations = grouped[tag]
                console.print(f"\n[bold]Operations in tag: {tag}[/bold]\n")
                display_operations_table(operations)
            else:
                console.print(f"[red]Tag '{tag}' not found[/red]")
                console.print(f"\nAvailable tags: {', '.join(sorted(grouped.keys()))}")
        else:
            display_operations_tree(grouped)
            console.print(
                f"\n[bold]Total:[/bold] {sum(len(ops) for ops in grouped.values())} operations in {len(grouped)} categories"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("generate")
def generate_commands(
    spec_path: Path = typer.Option(
        "docs/jira-openapi-v3.json",
        "--spec",
        "-s",
        help="Path to OpenAPI specification file",
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for generated files"
    ),
    tag: Optional[str] = typer.Option(
        None, "--tag", "-t", help="Generate commands only for specific tag"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Interactive mode for selection"
    ),
):
    """Generate CLI commands from OpenAPI specification"""
    try:
        # Determine base path
        base_path = Path.cwd()
        if output_dir:
            base_path = output_dir

        parser = OpenAPIParser(spec_path)
        generator = CommandGenerator(base_path)
        grouped = parser.group_operations_by_tag()

        console.print(
            "\n[bold cyan]OpenAPI CLI Command Generator[/bold cyan]"
        )
        console.print(f"Spec: {spec_path}")
        console.print(
            f"Found {sum(len(ops) for ops in grouped.values())} operations in {len(grouped)} categories\n"
        )

        if interactive:
            # Interactive mode: let user select tags/operations
            console.print("[bold]Available tags:[/bold]")
            tags_list = sorted(grouped.keys())
            for idx, tag_name in enumerate(tags_list, 1):
                console.print(f"  {idx}. {tag_name} ({len(grouped[tag_name])} operations)")

            if tag:
                selected_tags = [tag]
            else:
                selection = Prompt.ask(
                    "\nEnter tag numbers to generate (comma-separated, or 'all')",
                    default="all",
                )

                if selection.lower() == "all":
                    selected_tags = tags_list
                else:
                    try:
                        indices = [int(i.strip()) - 1 for i in selection.split(",")]
                        selected_tags = [tags_list[i] for i in indices if 0 <= i < len(tags_list)]
                    except (ValueError, IndexError):
                        console.print("[red]Invalid selection[/red]")
                        raise typer.Exit(1)

            # Confirm generation
            total_ops = sum(len(grouped[t]) for t in selected_tags)
            console.print(
                f"\n[yellow]Will generate {total_ops} commands in {len(selected_tags)} file(s)[/yellow]"
            )

            if not Confirm.ask("Proceed with generation?"):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

            # Generate commands
            console.print("\n[bold]Generating commands...[/bold]\n")
            generated_files = []

            for tag_name in selected_tags:
                operations = grouped[tag_name]
                code = generator.generate_command_group(tag_name, operations)
                file_path = generator.save_command_group(tag_name, code)
                generated_files.append(file_path)

            console.print(f"\n[bold green]✓ Successfully generated {len(generated_files)} command files[/bold green]")
            console.print("\n[yellow]Next steps:[/yellow]")
            console.print("1. Review the generated files")
            console.print("2. Register them in main.py if needed")
            console.print("3. Test the commands")

        else:
            # Non-interactive: generate for specified tag or all
            if tag:
                if tag not in grouped:
                    console.print(f"[red]Tag '{tag}' not found[/red]")
                    raise typer.Exit(1)
                selected_tags = [tag]
            else:
                selected_tags = list(grouped.keys())

            console.print(f"[bold]Generating commands for {len(selected_tags)} tag(s)...[/bold]\n")

            for tag_name in selected_tags:
                operations = grouped[tag_name]
                code = generator.generate_command_group(tag_name, operations)
                generator.save_command_group(tag_name, code)

            console.print("\n[bold green]✓ Done![/bold green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command("inspect")
def inspect_operation(
    operation_id: str = typer.Argument(..., help="Operation ID to inspect"),
    spec_path: Path = typer.Option(
        "docs/jira-openapi-v3.json",
        "--spec",
        "-s",
        help="Path to OpenAPI specification file",
    ),
):
    """Inspect a specific operation and show what would be generated"""
    try:
        parser = OpenAPIParser(spec_path)
        operations = parser.get_all_operations()

        # Find the operation
        operation = None
        for op in operations:
            if op["operationId"] == operation_id:
                operation = op
                break

        if not operation:
            console.print(f"[red]Operation '{operation_id}' not found[/red]")
            raise typer.Exit(1)

        # Display operation details
        console.print("\n[bold cyan]Operation Details[/bold cyan]\n")
        console.print(f"[bold]Operation ID:[/bold] {operation['operationId']}")
        console.print(f"[bold]Method:[/bold] {operation['method']}")
        console.print(f"[bold]Path:[/bold] {operation['path']}")
        console.print(f"[bold]Summary:[/bold] {operation['summary']}")
        console.print(f"[bold]Tags:[/bold] {', '.join(operation['tags'])}")

        if operation.get("parameters"):
            console.print("\n[bold]Parameters:[/bold]")
            for param in operation["parameters"]:
                console.print(f"  - {param['name']} ({param['in']}): {param.get('description', 'N/A')[:60]}")

        if operation.get("requestBody"):
            console.print("\n[bold]Request Body:[/bold] Yes")

        # Generate and display code
        generator = CommandGenerator(Path.cwd())
        code = generator.generate_command_code(operation)

        console.print("\n[bold cyan]Generated Code Preview[/bold cyan]\n")
        console.print(code)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
