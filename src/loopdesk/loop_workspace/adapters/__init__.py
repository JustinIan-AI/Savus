"""Adapter boundary implementations for cross-tool integration."""

from __future__ import annotations

from loopdesk.loop_workspace.adapters.mcp_client import McpClient
from typing import Any

from loopdesk.loop_workspace.repository import LoopWorkspaceRepository


class ToolEvent:
    def __init__(self, tool: str, name: str, payload: dict[str, Any]) -> None:
        self.tool = tool
        self.name = name
        self.payload = payload


class CrossToolAdapter:
    def __init__(self, repository: LoopWorkspaceRepository) -> None:
        self._repository = repository

    def translate_event_to_run_log(self, event: ToolEvent) -> dict[str, Any]:
        source = f"tool:{event.tool}"
        run_log = {
            "source": source,
            "status": "active",
            "summary": f"{event.tool}.{event.name} completed.",
            "workId": event.payload.get("workId"),
            "previousStatus": None,
            "payload": event.payload,
        }
        self._repository.append_run_log(run_log)
        return run_log

    def build_tool_context(self, state) -> dict[str, Any]:
        return {
            "workspaceRoot": state.workspace_root,
            "intent": state.intent,
            "currentWorkId": state.current_work_id,
            "selectedTemplate": state.selected_template,
            "memoryEnabled": True,
        }


class AcpToolAdapter:
    def __init__(self, repository: LoopWorkspaceRepository) -> None:
        self._repository = repository

    def translate_event_to_run_log(self, event: ToolEvent) -> dict[str, Any]:
        run_log = {
            "source": f"tool:acp:{event.tool}",
            "status": "active",
            "summary": f"{event.tool}.{event.name} queued via ACP placeholder.",
            "workId": event.payload.get("workId"),
            "previousStatus": None,
            "payload": {
                "status": "placeholder",
                "reason": "ACP integration is not implemented in v0.1.",
                "event": {"tool": event.tool, "name": event.name, "payload": event.payload},
            },
        }
        self._repository.append_run_log(run_log)
        return run_log


def translate_inbound(service, event: dict[str, Any]) -> dict[str, Any]:
    tool = event.get("tool") or event.get("source") or "tool"
    name = event.get("name") or event.get("command") or tool
    run_log = {
        "source": f"tool:{tool}",
        "workId": event.get("workId") or event.get("work_id"),
        "status": "active",
        "summary": event.get("summary") or f"{tool}.{name} completed.",
        "previousStatus": None,
        "toolEvent": event.get("toolEvent") or event,
    }
    service.record_run_log(run_log)
    if event.get("artifact"):
        service.record_run_log(
            {
                "source": f"tool:{tool}",
                "workId": run_log["workId"],
                "status": "active",
                "summary": f"{tool}.{name} artifact recorded.",
                "previousStatus": None,
                "toolEvent": {"artifact": event["artifact"]},
            }
        )
    return {"run_log": service.repository.read().run_log[-2:]}
