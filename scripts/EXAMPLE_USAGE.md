# Example: Generating and Using CLI Commands

This document demonstrates the complete workflow for generating CLI commands from the OpenAPI specification.

## Step 1: List Available Operations

First, let's see what operations are available:

```bash
# List all operations grouped by tags
uv run python scripts/generate_commands.py list

# List operations for a specific tag
uv run python scripts/generate_commands.py list --tag "Issues"
```

Output example:
```
Available API Operations
├── Issues (48 operations)
│   ├── GET Get issue
│   ├── POST Create issue
│   ├── PUT Edit issue
│   ├── DELETE Delete issue
│   └── ... and 44 more
├── Projects (23 operations)
│   ├── GET Get all projects
│   ├── POST Create project
│   └── ... and 21 more
...
```

## Step 2: Inspect a Specific Operation

Before generating, you can preview what code would be created:

```bash
uv run python scripts/generate_commands.py inspect getIssue
```

Output shows:
- Operation details (method, path, parameters)
- Generated Python code preview
- Parameter types and descriptions

## Step 3: Generate Commands

### Option A: Interactive Mode (Recommended for first-time users)

```bash
uv run python scripts/generate_commands.py generate
```

The script will:
1. Show all available tags with operation counts
2. Prompt you to select which tags to generate (enter numbers or 'all')
3. Show what will be generated and ask for confirmation
4. Generate the command files

Example interaction:
```
Available tags:
  1. Issues (48 operations)
  2. Projects (23 operations)
  3. Groups (8 operations)
  4. Users (15 operations)
  ...

Enter tag numbers to generate (comma-separated, or 'all'): 3

Will generate 8 commands in 1 file(s)

Proceed with generation? [y/n]: y

Generating commands...
✓ Generated: src/jira_cli/commands/generated_groups.py

✓ Successfully generated 1 command files
```

### Option B: Generate Specific Tag (Non-interactive)

```bash
uv run python scripts/generate_commands.py generate --tag Groups --no-interactive
```

### Option C: Generate Multiple Tags

```bash
# Interactive selection
uv run python scripts/generate_commands.py generate
# Then enter: 1,3,5

# Or use the script multiple times for specific tags
uv run python scripts/generate_commands.py generate --tag Issues --no-interactive
uv run python scripts/generate_commands.py generate --tag Projects --no-interactive
```

## Step 4: Review Generated Code

The generated file is saved to `src/jira_cli/commands/generated_groups.py`:

```python
"""CLI commands for Groups"""

import json
from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="Groups operations")

@app.command("get_group")
def get_group(
    groupname: Optional[str] = typer.Option(None, "--groupname", help="..."),
    group_id: Optional[str] = typer.Option(None, "--groupId", help="..."),
    expand: Optional[str] = typer.Option(None, "--expand", help="..."),
) -> None:
    """Returns a group.  **[Permissions](#permissions) required:..."""
    try:
        with get_client() as client:
            result = client._request(
                method="GET",
                endpoint="/rest/api/3/group",
                params={
                    "groupname": groupname,
                    "groupId": group_id,
                    "expand": expand
                }
            )
        print_json(result)
    except Exception as e:
        handle_error(e)
```

## Step 5: Integrate with Main CLI

To use the generated commands, register them in `src/jira_cli/main.py`:

```python
# Add import at the top
from jira_cli.commands import auth, field, issue, project, generated_groups

# Register the new command group
app.add_typer(generated_groups.app, name="groups")
```

Now you can use the commands:

```bash
# See available group commands
jira-cli groups --help

# Use a specific command
jira-cli groups get-group --groupname "jira-administrators"

# Create a new group
jira-cli groups create-group --body '{"name":"developers"}'

# List users in a group
jira-cli groups get-users-from-group --groupname "developers"
```

## Step 6: Test Generated Commands

Verify the generated commands work correctly:

```bash
# Check for syntax errors
uv run python -m py_compile src/jira_cli/commands/generated_groups.py

# Run linter
uv run ruff check src/jira_cli/commands/generated_groups.py

# Test help output (doesn't require authentication)
uv run jira-cli groups --help
uv run jira-cli groups get-group --help
```

## Complete Example: Generate Commands for Multiple Categories

Let's generate commands for several common operations:

```bash
# 1. Generate commands for Issues
uv run python scripts/generate_commands.py generate --tag Issues --no-interactive

# 2. Generate commands for Projects  
uv run python scripts/generate_commands.py generate --tag Projects --no-interactive

# 3. Generate commands for Users
uv run python scripts/generate_commands.py generate --tag Users --no-interactive

# 4. Generate commands for Groups
uv run python scripts/generate_commands.py generate --tag Groups --no-interactive
```

Now register them all in `main.py`:

```python
from jira_cli.commands import (
    auth, 
    field, 
    issue, 
    project,
    generated_issues,
    generated_projects,
    generated_users,
    generated_groups,
)

# Register all command groups
app.add_typer(auth.app, name="auth")
app.add_typer(field.app, name="field")
app.add_typer(issue.app, name="issue")
app.add_typer(project.app, name="project")
app.add_typer(generated_issues.app, name="issues-ext")
app.add_typer(generated_projects.app, name="projects-ext")
app.add_typer(generated_users.app, name="users")
app.add_typer(generated_groups.app, name="groups")
```

## Tips and Best Practices

1. **Start Small**: Generate one or two tags first to test the workflow
2. **Review Generated Code**: Always review before committing
3. **Customize as Needed**: Feel free to modify generated code
4. **Use Meaningful Names**: When registering, choose clear command group names
5. **Test Thoroughly**: Verify commands work with your Jira instance
6. **Document Changes**: Update README with new command groups

## Common Patterns

### Pattern 1: Extend Existing Commands

If you already have manual commands for Issues, you can generate additional ones:

```bash
# Generate to see what's available
uv run python scripts/generate_commands.py list --tag Issues

# Generate them as an extension
uv run python scripts/generate_commands.py generate --tag Issues --no-interactive

# Register as "issues-advanced" or similar
app.add_typer(generated_issues.app, name="issues-advanced")
```

### Pattern 2: Generate New Categories

For operations not yet covered:

```bash
# See what categories are available
uv run python scripts/generate_commands.py list | grep "operations)"

# Generate new categories
uv run python scripts/generate_commands.py generate --tag "Dashboards" --no-interactive
uv run python scripts/generate_commands.py generate --tag "Filters" --no-interactive
```

### Pattern 3: Selective Generation

Use inspect to preview, then generate only what you need:

```bash
# Inspect specific operations
uv run python scripts/generate_commands.py inspect createDashboard
uv run python scripts/generate_commands.py inspect getDashboard

# If looks good, generate the whole category
uv run python scripts/generate_commands.py generate --tag Dashboards --no-interactive
```

## Troubleshooting

### Generated commands have issues?
- Check the OpenAPI spec for that operation
- Manually adjust the generated code if needed
- Report patterns that don't work well

### Want different naming?
- Modify the generated file after creation
- Or customize the generator's `generate_command_name()` method

### Need custom logic?
- Generate the base code
- Add custom validation or transformations
- Keep the generator output as a starting point

## Next Steps

After generating commands:

1. ✅ Test the commands with your Jira instance
2. ✅ Add any custom validation or logic
3. ✅ Update documentation
4. ✅ Commit the generated files
5. ✅ Consider contributing improvements to the generator
