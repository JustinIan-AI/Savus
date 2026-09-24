from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from loopdesk.gateway.app import create_gateway_app
from loopdesk.gateway.config import GatewayConfig
from loopdesk.loop_workspace.service import LoopWorkspaceService

def test_gateway_connector_routes(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Connector Workspace")
    client = TestClient(create_gateway_app(GatewayConfig()))
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"fields": {"summary": "Test Jira", "status": {"name": "Done"}, "description": "desc"}}'
    mock_resp.__enter__.return_value = mock_resp
    
    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.get("/api/v1/connectors/tasks?source=jira&remote_id=PROJ-1")
        assert res.status_code == 200
        data = res.json()
        assert data["ok"] is True
        assert data["task"]["title"] == "Test Jira"


def test_connector_rejects_query_token(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Connector Workspace")
    client = TestClient(create_gateway_app(GatewayConfig()))
    res = client.get("/api/v1/connectors/tasks?source=jira&remote_id=PROJ-101&token=leak-in-query")
    assert res.status_code == 400
    assert res.json()["code"] == "INSECURE_QUERY_TOKEN"
