# OpenAPI CLI Generator - Live Demonstration

## Step 1: List Available Operations

### Command:
```bash
uv run python scripts/generate_commands.py list --tag "Groups"
```

### Output:

Operations in tag: Groups

                                    Selected Operations                                     
┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #    ┃ Method ┃ Path                      ┃ Operation ID        ┃ Summary                ┃
┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ DELETE │ /rest/api/3/group         │ removeGroup         │ Remove group           │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 2    │ GET    │ /rest/api/3/group         │ getGroup            │ Get group              │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 3    │ POST   │ /rest/api/3/group         │ createGroup         │ Create group           │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 4    │ GET    │ /rest/api/3/group/bulk    │ bulkGetGroups       │ Bulk get groups        │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 5    │ GET    │ /rest/api/3/group/member  │ getUsersFromGroup   │ Get users from group   │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 6    │ DELETE │ /rest/api/3/group/user    │ removeUserFromGroup │ Remove user from group │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 7    │ POST   │ /rest/api/3/group/user    │ addUserToGroup      │ Add user to group      │
├──────┼────────┼───────────────────────────┼─────────────────────┼────────────────────────┤
│ 8    │ GET    │ /rest/api/3/groups/picker │ findGroups          │ Find groups            │
└──────┴────────┴───────────────────────────┴─────────────────────┴────────────────────────┘

---

## Step 2: Inspect a Specific Operation

### Command:
```bash
uv run python scripts/generate_commands.py inspect getGroup
```

### Output:

Operation Details

Operation ID: getGroup
Method: GET
Path: /rest/api/3/group
Summary: Get group
Tags: Groups

Parameters:
  - groupname (query): As a group's name can change, use of `groupId` is recommende
  - groupId (query): The ID of the group. This parameter cannot be used with the 
  - expand (query): List of fields to expand.

Generated Code Preview


@app.command("get_group")
def get_group(
    groupname: Optional = typer.Option(None, "--groupname", help="As a group's name can change, use of `groupId` is 
recommended to identify a group.   The name of the group. This parameter cannot be used with the `groupId` parameter."),
    group_id: Optional = typer.Option(None, "--groupId", help="The ID of the group. This parameter cannot be used with 
the `groupName` parameter."),
    expand: Optional = typer.Option(None, "--expand", help="List of fields to expand."),
) -> None:
    """This operation is deprecated, use [`group/member`](#api-rest-api-3-group-member-get).  Returns all users in a 
group.  **[Permissions](#permissions) required:** either of:   *  *Browse users and gro..."""
    try:
        with get_client() as client:
            result = client._request(method="GET", endpoint="/rest/api/3/group", params={"groupname": groupname, 
"groupId": group_id, "expand": expand})
        print_json(result)
    except Exception as e:
        handle_error(e)


---

## Step 3: Generate Commands

### Command:
```bash
uv run python scripts/generate_commands.py generate --tag "Groups" --no-interactive
```

### Output:

OpenAPI CLI Command Generator
Spec: docs/jira-openapi-v3.json
Found 597 operations in 97 categories

Generating commands for 1 tag(s)...

✓ Generated: /home/runner/work/jira-cli/jira-cli/src/jira_cli/commands/generated_groups.py

✓ Done!

---

## Step 4: Verify Generated Code

### Generated File Preview:
```python
"""CLI commands for Groups"""

import json
from typing import Optional

import typer

from jira_cli.commands.utils import get_client, handle_error, print_json

app = typer.Typer(help="Groups operations")

@app.command("remove_group")
def remove_group(
    groupname: Optional[str] = typer.Option(None, "--groupname", help=""),
    group_id: Optional[str] = typer.Option(None, "--groupId", help="The ID of the group. This parameter cannot be used with the `groupname` parameter."),
    swap_group: Optional[str] = typer.Option(None, "--swapGroup", help="As a group's name can change, use of `swapGroupId` is recommended to identify a group.   The group to transfer restrictions to. Only comments and worklogs are transferred. If restrictions are not t..."),
    swap_group_id: Optional[str] = typer.Option(None, "--swapGroupId", help="The ID of the group to transfer restrictions to. Only comments and worklogs are transferred. If restrictions are not transferred, comments and worklogs are inaccessible after the deletion. This par..."),
) -> None:
    """Deletes a group.  **[Permissions](#permissions) required:** Site administration (that is, member of the *site-admin* strategic [group](https://confluence.atlassian.com/x/24xjL))."""
    try:
        with get_client() as client:
            result = client._request(method="DELETE", endpoint="/rest/api/3/group", params={"groupname": groupname, "groupId": group_id, "swapGroup": swap_group, "swapGroupId": swap_group_id})
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("create_group")
def create_group(
    body: Optional[str] = typer.Option(None, "--body", "-b", help="JSON request body"),
) -> None:
    """Creates a group.  **[Permissions](#permissions) required:** Site administration (that is, member of the *site-admin* [group](https://confluence.atlassian.com/x/24xjL))."""
    try:
        with get_client() as client:
            result = client._request(method="POST", endpoint="/rest/api/3/group", json=json.loads(body) if body else None)
        print_json(result)
    except Exception as e:
        handle_error(e)


@app.command("bulk_get_groups")
def bulk_get_groups(
    start_at: Optional[int] = typer.Option(None, "--startAt", help="The index of the first item to return in a page of results (page offset)."),
    max_results: Optional[int] = typer.Option(None, "--maxResults", help="The maximum number of items to return per page."),
    group_id: Optional[str] = typer.Option(None, "--groupId", help="The ID of a group. To specify multiple IDs, pass multiple `groupId` parameters. For example, `groupId=5b10a2844c20165700ede21g&groupId=5b10ac8d82e05b22cc7d4ef5`."),
    group_name: Optional[str] = typer.Option(None, "--groupName", help="The name of a group. To specify multiple names, pass multiple `groupName` parameters. For example, `groupName=administrators&groupName=jira-software-users`."),
    access_type: Optional[str] = typer.Option(None, "--accessType", help="The access level of a group. Valid values: 'site-admin', 'admin', 'user'."),
    application_key: Optional[str] = typer.Option(None, "--applicationKey", help="The application key of the product user groups to search for. Valid values: 'jira-servicedesk', 'jira-software', 'jira-product-discovery', 'jira-core'."),
) -> None:
    """Returns a [paginated](#pagination) list of groups.  **[Permissions](#permissions) required:** *Browse users and groups* [global permission](https://confluence.atlassian.com/x/x4dKLg)."""
```

### Validation Results:
- Syntax Check: ✓ PASSED
- Linting Check: All checks passed!
✓ PASSED
- Line Count: 123 lines
