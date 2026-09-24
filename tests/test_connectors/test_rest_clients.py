from __future__ import annotations

from unittest.mock import patch, MagicMock
from loopdesk.connectors.task_source import JiraRestAdapter, PlaneRestAdapter
from loopdesk.connectors.knowledge_source import ConfluenceRestAdapter

def test_jira_rest_client():
    adapter = JiraRestAdapter(base_url="https://jira.example.com", api_token="secret")
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"fields": {"summary": "Fix P0 bug", "status": {"name": "In Progress"}, "description": "Details here"}}'
    mock_resp.__enter__.return_value = mock_resp
    
    with patch("urllib.request.urlopen", return_value=mock_resp):
        task = adapter.fetch_task("PROJ-101")
        assert task is not None
        assert task.remote_id == "PROJ-101"
        assert task.title == "Fix P0 bug"
        assert task.status == "In Progress"
        assert task.source == "jira"

def test_plane_rest_client():
    adapter = PlaneRestAdapter(base_url="https://plane.example.com", workspace_slug="team", project_id="p-1", api_key="key")
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"name": "Plane Issue", "state": {"name": "Done"}, "description_html": "<p>Done</p>"}'
    mock_resp.__enter__.return_value = mock_resp
    
    with patch("urllib.request.urlopen", return_value=mock_resp):
        task = adapter.fetch_task("ISSUE-42")
        assert task is not None
        assert task.title == "Plane Issue"
        assert task.status == "Done"

def test_confluence_rest_client():
    adapter = ConfluenceRestAdapter(base_url="https://wiki.example.com", api_token="wiki_key")
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"title": "System Architecture", "body": {"storage": {"value": "<p>Arch doc</p>"}}}'
    mock_resp.__enter__.return_value = mock_resp
    
    with patch("urllib.request.urlopen", return_value=mock_resp):
        doc = adapter.fetch_doc("12345")
        assert "# System Architecture" in doc
        assert "<p>Arch doc</p>" in doc
