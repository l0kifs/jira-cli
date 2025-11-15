# jira-cli

A lightweight CLI client for Jira Cloud REST API v3. This tool provides a simple command-line interface that closely mirrors the Jira REST API, making it easy to interact with Jira from your terminal.

## Features

- **Secure Authentication**: 
  - Secure credential storage using OS-native keychains (macOS Keychain, Windows Credential Locker, Linux Secret Service)
  - Simple API token-based authentication
  - Environment variable support for CI/CD and automation
- **Issue Management**:
  - Create, get, and update issues
  - Search issues using JQL
  - Get issue comments
  - Get issue history/changelog
- **Status Transitions**: Change issue statuses through workflow transitions
- **Project Operations**:
  - List all projects
  - Get project create metadata
- **Field Operations**:
  - List all fields
  - Search fields

## Installation

### From PyPI (when published)

```bash
pip install jira-cli
```

### From source

```bash
pip install -e .
```

## Configuration

### Secure Credential Storage (Recommended)

The easiest and most secure way to use jira-cli is to store your credentials securely using the system keyring:

```bash
jira-cli auth login
```

This will prompt you for your Jira credentials and store them securely in your system's native credential store:
- **macOS**: Keychain
- **Windows**: Windows Credential Locker
- **Linux**: Secret Service (GNOME Keyring, KWallet, etc.)

Your credentials are encrypted by the operating system and never stored in plain text.

**Note**: You can generate an API token from your Atlassian account settings: https://id.atlassian.com/manage-profile/security/api-tokens

#### Managing Credentials

```bash
# Check authentication status
jira-cli auth status

# Update credentials
jira-cli auth update

# Logout (delete stored credentials)
jira-cli auth logout
```

### Alternative: Environment Variables

You can also set up credentials using environment variables or a `.env` file:

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

## Usage

### General Help

```bash
jira-cli --help
```

### Version

```bash
jira-cli version
```

Show version information

### Authentication Commands

#### Login and store credentials securely

```bash
# Interactive prompt
jira-cli auth login

# Or provide credentials directly
jira-cli auth login --domain your-domain.atlassian.net --email your-email@example.com --api-token your-token
```

#### Check authentication status

```bash
jira-cli auth status
```

#### Update credentials

```bash
# Interactive update (shows current values)
jira-cli auth update

# Or update specific fields
jira-cli auth update --domain new-domain.atlassian.net
jira-cli auth update --email new-email@example.com
```

#### Logout (delete credentials)

```bash
# With confirmation prompt
jira-cli auth logout

# Skip confirmation
jira-cli auth logout --force
```

### Field Commands

#### List all fields

```bash
jira-cli field list
```

#### Search fields

```bash
jira-cli field search "summary"
```

### Project Commands

#### List all projects

```bash
jira-cli project list
```

#### Get project create metadata

```bash
jira-cli project create-meta PROJECT_KEY
jira-cli project create-meta PROJECT_KEY --issue-type 10001
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
- `GET /rest/api/3/field` - Get fields
- `GET /rest/api/3/field/search` - Search fields

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

## Publishing to PyPI

This project uses [UV](https://docs.astral.sh/uv/) as the package manager and GitHub Actions for automated publishing to PyPI.

### Prerequisites

1. **PyPI Account**: Create an account at [https://pypi.org/](https://pypi.org/)
2. **Trusted Publishing**: Configure trusted publishing (no API tokens needed!) at [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
   - Add a new publisher with:
     - PyPI Project Name: `jira-cli`
     - Owner: `l0kifs`
     - Repository name: `jira-cli`
     - Workflow name: `publish-to-pypi.yml`
     - Environment name: (leave blank)

### Automated Publishing (Recommended)

The project is configured to automatically publish to PyPI when a new GitHub release is created:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"  # Update to your new version
   ```

2. **Commit and push** your changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create a GitHub release**:
   - Go to [https://github.com/l0kifs/jira-cli/releases/new](https://github.com/l0kifs/jira-cli/releases/new)
   - Create a new tag (e.g., `v0.2.0`)
   - Add release title and description
   - Click "Publish release"

4. **GitHub Actions will automatically**:
   - Build the package using UV
   - Publish to PyPI using trusted publishing
   - You can monitor the progress in the Actions tab

### Manual Publishing

If you need to publish manually:

1. **Install UV** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Build the package**:
   ```bash
   uv build
   ```
   This creates distribution files in the `dist/` directory.

3. **Publish using UV** (requires PyPI API token):
   ```bash
   uv publish
   ```
   Or use `twine`:
   ```bash
   pip install twine
   twine upload dist/*
   ```

### Testing on TestPyPI

Before publishing to the main PyPI, you can test on TestPyPI:

1. Configure trusted publishing for TestPyPI at [https://test.pypi.org/manage/account/publishing/](https://test.pypi.org/manage/account/publishing/)

2. Manually trigger the workflow or modify the workflow to publish to TestPyPI:
   ```bash
   uv publish --index-url https://test.pypi.org/legacy/
   ```

3. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ jira-cli
   ```

## License

MIT