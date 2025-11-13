# jira-cli

A lightweight CLI client for Jira Cloud REST API v3. This tool provides a simple command-line interface that closely mirrors the Jira REST API, making it easy to interact with Jira from your terminal.

## Features

- **Authentication**: Simple API token-based authentication
- **Issue Management**:
  - Create, get, and update issues
  - Search issues using JQL
  - Get issue comments
  - Get issue history/changelog
- **Status Transitions**: Change issue statuses through workflow transitions
- **Project Operations**:
  - List all projects
  - Get project issue fields (create metadata)

## Installation

```bash
pip install -e .
```

## Configuration

Set up your Jira credentials using environment variables or a `.env` file:

```bash
# Environment variables
export JIRA_CLI__JIRA_DOMAIN="your-domain.atlassian.net"
export JIRA_CLI__JIRA_EMAIL="your-email@example.com"
export JIRA_CLI__JIRA_API_TOKEN="your-api-token"
```

Or create a `.env` file:

```env
JIRA_CLI__JIRA_DOMAIN=your-domain.atlassian.net
JIRA_CLI__JIRA_EMAIL=your-email@example.com
JIRA_CLI__JIRA_API_TOKEN=your-api-token
```

**Note**: You can generate an API token from your Atlassian account settings: https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

### General Help

```bash
jira-cli --help
```

### Project Commands

#### List all projects

```bash
jira-cli project list
```

#### Get project issue fields

```bash
jira-cli project fields PROJECT_KEY
jira-cli project fields PROJECT_KEY --issue-type 10001
```

### Issue Commands

#### Get issue details

```bash
jira-cli issue get PROJ-123
jira-cli issue get PROJ-123 --fields summary,status,assignee
jira-cli issue get PROJ-123 --expand changelog
```

#### Create an issue

```bash
jira-cli issue create --fields '{"project":{"key":"PROJ"},"summary":"Bug title","description":{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Description here"}]}]},"issuetype":{"name":"Bug"}}'
```

#### Update an issue

```bash
# Simple field update
jira-cli issue update PROJ-123 --fields '{"summary":"Updated title"}'

# Complex update with operations
jira-cli issue update PROJ-123 --update '{"labels":[{"add":"urgent"}]}'
```

#### Search issues using JQL

```bash
jira-cli issue search "project = PROJ AND status = 'To Do'"
jira-cli issue search "assignee = currentUser()" --max-results 10
jira-cli issue search "project = PROJ" --fields summary,status --start-at 50
```

#### Get available transitions

```bash
jira-cli issue transitions PROJ-123
```

#### Transition issue to new status

```bash
jira-cli issue transition PROJ-123 21
jira-cli issue transition PROJ-123 21 --fields '{"resolution":{"name":"Done"}}'
```

#### Get issue comments

```bash
jira-cli issue comments PROJ-123
```

#### Get issue history/changelog

```bash
jira-cli issue changelog PROJ-123
jira-cli issue changelog PROJ-123 --max-results 50
```

## Architecture

The CLI is built with:

- **Python 3.12+**: Modern Python with type hints
- **Typer**: CLI framework for building command-line applications
- **httpx**: Modern HTTP client for API requests
- **Rich**: Beautiful terminal formatting
- **Pydantic**: Configuration management
- **Loguru**: Logging

### Project Structure

```
src/jira_cli/
├── api/
│   ├── __init__.py
│   └── client.py          # Jira REST API client
├── commands/
│   ├── __init__.py
│   ├── issue.py           # Issue commands
│   ├── project.py         # Project commands
│   └── utils.py           # Shared utilities
├── config/
│   ├── __init__.py
│   ├── settings.py        # Configuration management
│   └── logging.py         # Logging configuration
└── main.py                # CLI entry point
```

## API Coverage

This CLI implements the following Jira Cloud REST API v3 endpoints:

- `POST /rest/api/3/issue` - Create issue
- `GET /rest/api/3/issue/{issueIdOrKey}` - Get issue
- `PUT /rest/api/3/issue/{issueIdOrKey}` - Update issue
- `GET /rest/api/3/search` - Search issues (JQL)
- `GET /rest/api/3/project` - Get projects
- `GET /rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}` - Get create metadata
- `GET /rest/api/3/issue/{issueIdOrKey}/transitions` - Get transitions
- `POST /rest/api/3/issue/{issueIdOrKey}/transitions` - Transition issue
- `GET /rest/api/3/issue/{issueIdOrKey}/comment` - Get comments
- `GET /rest/api/3/issue/{issueIdOrKey}/changelog` - Get changelog

## Examples

### Create a bug with full details

```bash
jira-cli issue create --fields '{
  "project": {"key": "MYPROJ"},
  "summary": "Critical bug in login",
  "description": {
    "type": "doc",
    "version": 1,
    "content": [{
      "type": "paragraph",
      "content": [{
        "type": "text",
        "text": "Users cannot log in after the latest deployment."
      }]
    }]
  },
  "issuetype": {"name": "Bug"},
  "priority": {"name": "High"}
}'
```

### Find all bugs assigned to you

```bash
jira-cli issue search "project = MYPROJ AND issuetype = Bug AND assignee = currentUser() AND status != Done"
```

### Move issue through workflow

```bash
# First, get available transitions
jira-cli issue transitions PROJ-123

# Then transition using the ID
jira-cli issue transition PROJ-123 31
```

## License

MIT