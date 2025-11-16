# OpenAPI CLI Command Generator

This directory contains scripts for generating CLI commands from the Jira OpenAPI v3 specification.

## Overview

The `generate_commands.py` script automates the creation of CLI commands from OpenAPI specifications. It:

- Parses the OpenAPI JSON specification
- Extracts operation details (endpoints, parameters, descriptions)
- Generates Python/Typer command code
- Provides interactive selection of API operations to convert
- Creates properly formatted command files with documentation

## Features

- **Interactive Mode**: Select which API operations to generate commands for
- **Bulk Generation**: Generate commands for entire tags/categories at once
- **Code Preview**: Inspect what code would be generated before creating files
- **Auto-discovery**: Automatically parses all operations from OpenAPI spec
- **Type Safety**: Generates proper Python type hints
- **Documentation**: Extracts and includes descriptions from OpenAPI spec

## Installation

The script uses the same dependencies as the main project. Make sure you've run:

```bash
uv sync
```

## Usage

### List Available Operations

View all available API operations grouped by tags:

```bash
uv run python scripts/generate_commands.py list
```

Filter by a specific tag:

```bash
uv run python scripts/generate_commands.py list --tag Issues
```

### Inspect a Specific Operation

Preview the code that would be generated for a specific operation:

```bash
uv run python scripts/generate_commands.py inspect getIssue
```

This shows:
- Operation details (method, path, parameters)
- Generated Python code preview

### Generate Commands

#### Interactive Mode (Default)

Generate commands with interactive selection:

```bash
uv run python scripts/generate_commands.py generate
```

The script will:
1. Show all available tags
2. Let you select which tags to generate
3. Ask for confirmation
4. Generate command files

#### Generate for Specific Tag

Generate commands for a specific category:

```bash
uv run python scripts/generate_commands.py generate --tag Issues
```

#### Non-Interactive Mode

Generate all commands without prompts:

```bash
uv run python scripts/generate_commands.py generate --no-interactive
```

#### Custom Output Directory

Specify a different output directory:

```bash
uv run python scripts/generate_commands.py generate --output /path/to/output
```

## Generated Files

Generated command files are saved to:
```
src/jira_cli/commands/generated_{tag_name}.py
```

For example:
- `generated_issues.py` - Issue operations
- `generated_projects.py` - Project operations
- `generated_users.py` - User operations

## Generated Code Structure

Each generated file contains:

```python
"""CLI commands for {Tag}"""

import json
from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="{Tag} operations")


@app.command("command_name")
def function_name(
    param1: str = typer.Argument(..., help="Parameter description"),
    param2: Optional[str] = typer.Option(None, "--param2", help="Optional parameter"),
) -> None:
    """Operation description from OpenAPI spec"""
    try:
        with get_client() as client:
            result = client._request(
                method="GET",
                endpoint=f"/rest/api/3/endpoint/{param1}",
                params={"param2": param2}
            )
        print_json(result)
    except Exception as e:
        handle_error(e)
```

## Integrating Generated Commands

After generating command files, you need to register them in `main.py`:

```python
from jira_cli.commands import generated_issues

app.add_typer(generated_issues.app, name="issues-gen")
```

## Command Line Options

### List Command
- `--spec, -s`: Path to OpenAPI specification file (default: `docs/jira-openapi-v3.json`)
- `--tag, -t`: Filter by tag/category

### Generate Command
- `--spec, -s`: Path to OpenAPI specification file
- `--output, -o`: Output directory for generated files
- `--tag, -t`: Generate commands only for specific tag
- `--interactive/--no-interactive`: Enable/disable interactive mode (default: interactive)

### Inspect Command
- `operation_id`: The OpenAPI operation ID to inspect
- `--spec, -s`: Path to OpenAPI specification file

## Examples

### Example 1: Generate Commands for Multiple Tags

```bash
# Run in interactive mode
uv run python scripts/generate_commands.py generate

# Select tags:
# Enter tag numbers to generate (comma-separated, or 'all'): 1,3,5
```

### Example 2: Preview Before Generating

```bash
# Inspect what would be generated
uv run python scripts/generate_commands.py inspect createIssue

# If looks good, generate it
uv run python scripts/generate_commands.py generate --tag Issues
```

### Example 3: Generate All Commands

```bash
# Generate everything at once (careful - generates 400+ operations!)
uv run python scripts/generate_commands.py generate --no-interactive
```

## Customization

The generator can be customized by modifying the `CommandGenerator` class in `generate_commands.py`:

- **Function naming**: Modify `generate_function_name()` 
- **Command naming**: Modify `generate_command_name()`
- **Parameter handling**: Modify `generate_parameter_definition()`
- **Code templates**: Modify `generate_command_code()`

## Tips

1. **Start Small**: Begin by generating commands for a single tag to test
2. **Review Generated Code**: Always review generated files before committing
3. **Test Commands**: Test generated commands to ensure they work correctly
4. **Incremental Generation**: Generate commands incrementally rather than all at once
5. **Custom Modifications**: Feel free to modify generated code as needed

## Troubleshooting

### Issue: Generated commands have syntax errors
- Check that the OpenAPI spec is valid JSON
- Review the generated code for any edge cases
- Report issues with specific operations that fail

### Issue: Parameters not generating correctly
- Some complex parameter types may need manual adjustment
- Arrays are simplified to comma-separated strings
- Check the OpenAPI spec for parameter schema details

### Issue: Descriptions are truncated
- Long descriptions are automatically truncated to 200 characters
- Edit the generated file to add full descriptions if needed

## Architecture

The generator consists of three main classes:

1. **OpenAPIParser**: Parses and extracts operations from OpenAPI spec
2. **CommandGenerator**: Generates Python/Typer command code
3. **CLI Interface**: Provides interactive and non-interactive modes

The workflow:
1. Parse OpenAPI spec
2. Group operations by tags
3. Let user select operations (if interactive)
4. Generate code for each operation
5. Save to files with proper formatting

## Future Enhancements

Potential improvements:
- Support for custom templates
- Configuration file for generator settings
- Dry-run mode to preview file changes
- Integration with code formatters (black, ruff)
- Support for OAuth and other auth methods
- Automatic registration in main.py
