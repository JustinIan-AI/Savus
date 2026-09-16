"""Tool boundary re-export for callers that import through loopdesk.tools."""

from __future__ import annotations

from loopdesk.tool_boundary import AgentToolHandler, ToolCall, ToolResult

__all__ = ["AgentToolHandler", "ToolCall", "ToolResult"]
