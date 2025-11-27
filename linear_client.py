"""
Linear Client for FocusFlow.
Handles integration with Linear API (or MCP server) for task synchronization.
Falls back to mock data if no API key is provided.
"""
import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime

class LinearClient:
    """Client for interacting with Linear."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Linear client."""
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        self.api_url = "https://api.linear.app/graphql"
        self.is_active = bool(self.api_key)

        if not self.is_active:
            print("ℹ️ Linear: No API key found. Using mock data.")

    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }

    def _query(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query."""
        if not self.is_active:
            return {}

        try:
            response = requests.post(
                self.api_url,
                headers=self._headers(),
                json={"query": query, "variables": variables or {}}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Linear API error: {e}")
            return {}

    def get_user_projects(self) -> List[Dict]:
        """Get projects for the current user."""
        if not self.is_active:
            return [
                {"id": "mock-1", "name": "Website Redesign", "description": "Overhaul the company website"},
                {"id": "mock-2", "name": "Mobile App", "description": "iOS and Android app development"},
                {"id": "mock-3", "name": "API Migration", "description": "Migrate legacy API to GraphQL"}
            ]

        query = """
        query {
            viewer {
                projects(first: 10) {
                    nodes {
                        id
                        name
                        description
                    }
                }
            }
        }
        """
        result = self._query(query)
        try:
            return result.get("data", {}).get("viewer", {}).get("projects", {}).get("nodes", [])
        except Exception:
            return []

    def get_project_tasks(self, project_id: str) -> List[Dict]:
        """Get tasks for a specific project."""
        if not self.is_active:
            # Return mock tasks based on project ID
            if project_id == "mock-1":
                return [
                    {"id": "L-101", "title": "Design Homepage", "description": "Create Figma mockups", "estimate": 60},
                    {"id": "L-102", "title": "Implement Header", "description": "React component for header", "estimate": 30},
                    {"id": "L-103", "title": "Fix CSS Bugs", "description": "Fix mobile layout issues", "estimate": 45}
                ]
            return [
                {"id": "L-201", "title": "Setup Repo", "description": "Initialize git repository", "estimate": 15},
                {"id": "L-202", "title": "Basic Auth", "description": "Implement login flow", "estimate": 60}
            ]

        query = """
        query($projectId: ID!) {
            project(id: $projectId) {
                issues(first: 20, filter: { state: { name: { neq: "Done" } } }) {
                    nodes {
                        id
                        title
                        description
                        estimate
                    }
                }
            }
        }
        """
        result = self._query(query, {"projectId": project_id})
        try:
            return result.get("data", {}).get("project", {}).get("issues", {}).get("nodes", [])
        except Exception:
            return []

    def create_task(self, title: str, description: str = "", team_id: str = None) -> Optional[str]:
        """Create a new task (issue) in Linear."""
        if not self.is_active:
            print(f"ℹ️ Linear (Mock): Created task '{title}'")
            return "mock-new-id"

        # Note: This requires a team_id. For simplicity, we might need to fetch a default team first.
        # This is a simplified implementation.
        if not team_id:
            # Try to get the first team
            team_query = """query { viewer { teams(first: 1) { nodes { id } } } }"""
            team_res = self._query(team_query)
            try:
                team_id = team_res["data"]["viewer"]["teams"]["nodes"][0]["id"]
            except:
                return None

        mutation = """
        mutation($title: String!, $description: String, $teamId: String!) {
            issueCreate(input: { title: $title, description: $description, teamId: $teamId }) {
                issue {
                    id
                }
            }
        }
        """
        result = self._query(mutation, {"title": title, "description": description, "teamId": team_id})
        try:
            return result["data"]["issueCreate"]["issue"]["id"]
        except:
            return None
