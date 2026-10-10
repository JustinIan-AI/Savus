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


def test_mcp_connector_lifecycle_routes(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test MCP Workspace")
    client = TestClient(create_gateway_app(GatewayConfig()))

    # 1. Register & start MCP server
    res_reg = client.post("/api/v1/connectors/mcp/register", json={
        "name": "test-cat-mcp",
        "command": "cat",
        "args": []
    })
    assert res_reg.status_code == 200
    assert res_reg.json()["ok"] is True
    assert res_reg.json()["state"] == "running"

    # 2. Check status
    res_stat = client.get("/api/v1/connectors/mcp/test-cat-mcp/status")
    assert res_stat.status_code == 200
    assert res_stat.json()["state"] == "running"

    # 3. Record tool trace
    res_trace = client.post("/api/v1/connectors/mcp/test-cat-mcp/trace", json={
        "tool_name": "cat_file",
        "params": {"path": "/tmp/test.txt"},
        "duration_ms": 12,
        "token_cost": 50
    })
    assert res_trace.status_code == 200
    trace_id = res_trace.json()["trace_id"]
    assert trace_id is not None

    # 4. List traces
    res_traces = client.get("/api/v1/connectors/mcp/test-cat-mcp/traces")
    assert res_traces.status_code == 200
    traces = res_traces.json()["traces"]
    assert len(traces) == 1
    assert traces[0]["tool_name"] == "cat_file"

    # 5. Stop server
    res_stop = client.post("/api/v1/connectors/mcp/test-cat-mcp/stop")
    assert res_stop.status_code == 200
    assert res_stop.json()["ok"] is True

    # 6. Verify state is offline
    res_stat2 = client.get("/api/v1/connectors/mcp/test-cat-mcp/status")
    assert res_stat2.json()["state"] == "offline"
