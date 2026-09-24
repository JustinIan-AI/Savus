from __future__ import annotations

import pytest
from loopdesk.connectors.mcp_manager import MCPConnectorManager, MCPCallTracer, MCPServerState

def test_mcp_hot_reload_and_circuit_breaker():
    manager = MCPConnectorManager()

    # Register an MCP server
    manager.register_server("jira-mcp", command="uvx", args=["mcp-jira"])
    assert manager.get_server_state("jira-mcp") == MCPServerState.IDLE

    # Record failures to trip circuit breaker
    manager.record_failure("jira-mcp")
    manager.record_failure("jira-mcp")
    manager.record_failure("jira-mcp")

    assert manager.get_server_state("jira-mcp") == MCPServerState.CIRCUIT_BROKEN
    assert manager.is_available("jira-mcp") is False

    # Hot-reload / reset server
    manager.reload_server("jira-mcp")
    assert manager.get_server_state("jira-mcp") == MCPServerState.IDLE
    assert manager.is_available("jira-mcp") is True

def test_mcp_tool_call_traceability():
    tracer = MCPCallTracer()

    trace_id = tracer.record_call(
        server_name="jira-mcp",
        tool_name="get_issue",
        params={"issue_key": "PROJ-101"},
        duration_ms=45,
        token_cost=120
    )

    traces = tracer.get_traces_for_server("jira-mcp")
    assert len(traces) == 1
    assert traces[0]["trace_id"] == trace_id
    assert traces[0]["tool_name"] == "get_issue"
    assert traces[0]["token_cost"] == 120
