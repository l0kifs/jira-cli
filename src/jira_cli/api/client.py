"""Jira REST API v3 client"""
import base64
from typing import Any, Optional

import httpx
from loguru import logger


class JiraClient:
    """Lightweight wrapper for Jira Cloud REST API v3"""

    def __init__(self, domain: str, email: str, api_token: str):
        """
        Initialize Jira client with authentication credentials.
        
        Args:
            domain: Jira instance domain (e.g., your-domain.atlassian.net)
            email: Email associated with Jira account
            api_token: API token for authentication
        """
        self.domain = domain.rstrip("/")
        self.base_url = f"https://{self.domain}/rest/api/3"
        self.email = email
        self.api_token = api_token
        
        # Create Basic Auth header
        auth_str = f"{email}:{api_token}"
        auth_bytes = auth_str.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        self.client = httpx.Client(headers=self.headers, timeout=30.0)
        logger.debug(f"Initialized Jira client for {self.base_url}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def _request(
        self, method: str, endpoint: str, params: Optional[dict] = None, json: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Make HTTP request to Jira API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., /issue)
            params: Query parameters
            json: JSON body for POST/PUT requests
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"{method} {url}")
        
        try:
            response = self.client.request(method, url, params=params, json=json)
            response.raise_for_status()
            
            # Return empty dict for 204 No Content responses
            if response.status_code == 204:
                return {}
            
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    # Issue operations
    def create_issue(self, fields: dict) -> dict:
        """
        Create a new issue.
        
        Args:
            fields: Issue fields as per Jira API
            
        Returns:
            Created issue data
        """
        return self._request("POST", "/issue", json={"fields": fields})

    def get_issue(self, issue_key: str, fields: Optional[str] = None, expand: Optional[str] = None) -> dict:
        """
        Get issue details.
        
        Args:
            issue_key: Issue ID or key (e.g., PROJ-123)
            fields: Comma-separated list of fields to return
            expand: Comma-separated list of parameters to expand
            
        Returns:
            Issue data
        """
        params = {}
        if fields:
            params["fields"] = fields
        if expand:
            params["expand"] = expand
        return self._request("GET", f"/issue/{issue_key}", params=params)

    def update_issue(self, issue_key: str, fields: Optional[dict] = None, update: Optional[dict] = None) -> dict:
        """
        Update an issue.
        
        Args:
            issue_key: Issue ID or key
            fields: Fields to update (simple updates)
            update: Update operations for complex fields
            
        Returns:
            Empty dict on success
        """
        body = {}
        if fields:
            body["fields"] = fields
        if update:
            body["update"] = update
        return self._request("PUT", f"/issue/{issue_key}", json=body)

    # Search
    def search_issues(self, jql: str, fields: Optional[str] = None, start_at: int = 0, max_results: int = 50) -> dict:
        """
        Search for issues using JQL.
        
        Args:
            jql: JQL query string
            fields: Comma-separated list of fields to return
            start_at: Index of first result to return
            max_results: Maximum number of results
            
        Returns:
            Search results with issues array
        """
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
        }
        if fields:
            params["fields"] = fields
        return self._request("GET", "/search", params=params)

    # Projects
    def get_projects(self) -> list[dict]:
        """
        Get all projects visible to user.
        
        Returns:
            List of projects
        """
        return self._request("GET", "/project")

    def get_create_metadata(self, project_key: str, issue_type_id: Optional[str] = None) -> dict:
        """
        Get issue create metadata for a project.
        
        Args:
            project_key: Project key
            issue_type_id: Optional issue type ID
            
        Returns:
            Create metadata including available fields
        """
        endpoint = f"/issue/createmeta/{project_key}"
        if issue_type_id:
            endpoint += f"/issuetypes/{issue_type_id}"
        return self._request("GET", endpoint)

    # Transitions
    def get_transitions(self, issue_key: str) -> dict:
        """
        Get available transitions for an issue.
        
        Args:
            issue_key: Issue ID or key
            
        Returns:
            Available transitions
        """
        return self._request("GET", f"/issue/{issue_key}/transitions")

    def transition_issue(self, issue_key: str, transition_id: str, fields: Optional[dict] = None) -> dict:
        """
        Transition an issue to a new status.
        
        Args:
            issue_key: Issue ID or key
            transition_id: ID of the transition to perform
            fields: Optional fields to update during transition
            
        Returns:
            Empty dict on success
        """
        body = {"transition": {"id": transition_id}}
        if fields:
            body["fields"] = fields
        return self._request("POST", f"/issue/{issue_key}/transitions", json=body)

    # Comments
    def get_comments(self, issue_key: str) -> dict:
        """
        Get comments for an issue.
        
        Args:
            issue_key: Issue ID or key
            
        Returns:
            Comments data
        """
        return self._request("GET", f"/issue/{issue_key}/comment")

    # History/Changelog
    def get_changelog(self, issue_key: str, start_at: int = 0, max_results: int = 100) -> dict:
        """
        Get changelog/history for an issue.
        
        Args:
            issue_key: Issue ID or key
            start_at: Index of first result to return
            max_results: Maximum number of results
            
        Returns:
            Changelog data
        """
        params = {
            "startAt": start_at,
            "maxResults": max_results,
        }
        return self._request("GET", f"/issue/{issue_key}/changelog", params=params)
