from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import json
import urllib.request
import urllib.error

class SyncDirection(str, Enum):
    PULL = "pull"
    PUSH = "push"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class RemoteTask:
    remote_id: str
    title: str
    status: str
    description: str = ""
    source: str = "remote"
    metadata: dict[str, Any] = field(default_factory=dict)

class TaskSourceAdapter(ABC):
    @abstractmethod
    def fetch_task(self, remote_id: str) -> RemoteTask | None:
        pass

    @abstractmethod
    def update_task_status(self, remote_id: str, status: str) -> bool:
        pass

class JiraRestAdapter(TaskSourceAdapter):
    """Real REST API client for Jira Software (Cloud/Server)."""
    def __init__(self, base_url: str, api_token: str = "", email: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.email = email

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def fetch_task(self, remote_id: str) -> RemoteTask | None:
        url = f"{self.base_url}/rest/api/3/issue/{remote_id}"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    fields = data.get("fields", {})
                    summary = fields.get("summary", "")
                    status_obj = fields.get("status", {})
                    status_name = status_obj.get("name", "Unknown")
                    desc = fields.get("description", "")
                    if isinstance(desc, dict):
                        desc = str(desc)
                    return RemoteTask(
                        remote_id=remote_id,
                        title=summary,
                        status=status_name,
                        description=desc,
                        source="jira",
                        metadata=fields
                    )
        except Exception:
            return None
        return None

    def update_task_status(self, remote_id: str, status: str) -> bool:
        url = f"{self.base_url}/rest/api/3/issue/{remote_id}/transitions"
        payload = json.dumps({"transition": {"name": status}}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=self._get_headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status in (200, 204)
        except Exception:
            return False

class PlaneRestAdapter(TaskSourceAdapter):
    """Real REST API client for Plane.so issue tracker."""
    def __init__(self, base_url: str, workspace_slug: str, project_id: str, api_key: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.workspace_slug = workspace_slug
        self.project_id = project_id
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def fetch_task(self, remote_id: str) -> RemoteTask | None:
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_slug}/projects/{self.project_id}/issues/{remote_id}"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return RemoteTask(
                        remote_id=remote_id,
                        title=data.get("name", ""),
                        status=data.get("state", {}).get("name", "Open"),
                        description=data.get("description_html", ""),
                        source="plane",
                        metadata=data
                    )
        except Exception:
            return None
        return None

    def update_task_status(self, remote_id: str, status: str) -> bool:
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_slug}/projects/{self.project_id}/issues/{remote_id}"
        payload = json.dumps({"state": status}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=self._get_headers(), method="PATCH")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status in (200, 204)
        except Exception:
            return False
