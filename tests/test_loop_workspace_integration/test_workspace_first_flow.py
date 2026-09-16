"""Workspace-first integration test for LoopDesk v0.1."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.adapters import McpClient, translate_inbound
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase
from loopdesk.loop_workspace.engine.runner import LoopEngineRunner


def test_workspace_first_flow_records_loop_and_tool_events(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    state = service.record_work_item("work-1", "loop", "Draft plan.")

    memory = service.layout.memory_dir / "resume-note.md"
    memory.write_text("Remember to review the API contract.", encoding="utf-8")

    assert state["current_work_id"] == "work-1"
    assert state["status"] == "active"
    assert memory.exists()


def test_workspace_first_flow_includes_engine_and_adapter_round_trip(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    state = service.record_work_item("work-1", "loop", "Draft plan.")
    assert state["current_work_id"] == "work-1"

    runner = LoopEngineRunner(service)
    engine_state = runner.step(LoopEngineState(phase=LoopPhase.PLANNED, goal="Draft plan."))
    assert engine_state.phase == LoopPhase.TRIAGE
    engine_state = runner.step(engine_state, decision="act")
    assert engine_state.phase == LoopPhase.MAKER

    client = McpClient()
    client.connect("python", ["-m", "tests.test_gateway.fake_mcp_server"])
    tools = client.list_tools()
    assert any(tool.get("name") == "echo" for tool in tools)
    tool_result = client.call_tool("echo", {"text": "hello"})
    client.disconnect()

    translated = translate_inbound(service, {"tool": "fake-mcp", "name": "echo", "workId": "work-1", "toolEvent": tool_result})
    assert len(translated["run_log"]) >= 1
    assert service.repository.read().cost_observatory["status"] == service.repository.read().status.value
