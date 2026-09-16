"""Stdio MCP integration tests for LoopDesk workspace tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService
from tests.support.mcp_workspace_client import build_client, call_tool, initialize_client, list_tools


@pytest.fixture()
def mcp_workspace(tmp_path: Path) -> Path:
    layout = LoopWorkspaceLayout.ensure(tmp_path / "workspace")
    service = LoopWorkspaceService.from_root(layout.root)
    service.ensure_initialized(intent="MCP integration", selected_template="backend-engineer")
    service.record_work_item("work-1", "loop", "Validate MCP handoff.")
    service.set_kill_switch(True)
    service.set_denylist(["dangerous.sh"])
    return layout.root


@pytest.fixture()
def mcp_client(mcp_workspace: Path):
    client = build_client(mcp_workspace, in_process=True)
    initialize_client(client)
    yield client
    process = client.get("process")
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    server_thread = client.get("server_thread")
    if server_thread is not None:
        server_thread.join(timeout=5)


def test_mcp_server_exposes_workspace_context_and_templates(mcp_client: dict[str, object]) -> None:
    tools = list_tools(mcp_client)
    tool_names = [tool["name"] for tool in tools]

    assert tool_names == [
        "loopdesk.get_context_pack",
        "loopdesk.list_templates",
        "loopdesk.read_template",
        "loopdesk.run_local_command",
    ]

    context_pack = call_tool(mcp_client, "loopdesk.get_context_pack", {})
    templates = call_tool(mcp_client, "loopdesk.list_templates", {})

    assert context_pack["current_work_id"] == "work-1"
    assert context_pack["selected_template"] == "backend-engineer"
    assert context_pack["safety"]["kill_switch_enabled"] is True
    assert context_pack["safety"]["denylist"] == ["dangerous.sh"]
    assert any(template["id"] == "backend-engineer" for template in templates["templates"])


def test_mcp_server_reads_template_and_records_command(mcp_client: dict[str, object]) -> None:
    template = call_tool(mcp_client, "loopdesk.read_template", {"template_id": "backend-engineer"})
    result = call_tool(mcp_client, "loopdesk.run_local_command", {"argv": ["printf", "mcp-handoff\n"], "work_id": "work-1"})

    assert template["name"] == "Backend Implementation"
    assert template["loop_steps"][0] == "Review failing tests, issues, and task backlog."
    assert result["ok"] is True
    assert result["stdout"].strip() == "mcp-handoff"
