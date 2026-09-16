"""LoopDesk personal workspace MCP server."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.templates import list_personal_templates, load_personal_template
from loopdesk.loop_workspace.schema import serialize_json_payload


def _workspace_root() -> Path:
    root = os.environ.get("LOOPDESK_WORKSPACE")
    if not root:
        raise RuntimeError("Set LOOPDESK_WORKSPACE to a LoopDesk workspace root.")
    return Path(root)


def _build_tools() -> list[Tool]:
    return [
        Tool(
            name="loopdesk.get_context_pack",
            description="Return the current LoopDesk context pack for the workspace.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="loopdesk.list_templates",
            description="List personal workflow templates available in the workspace.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="loopdesk.read_template",
            description="Read a personal workflow template by id.",
            inputSchema={
                "type": "object",
                "properties": {"template_id": {"type": "string"}},
                "required": ["template_id"],
            },
        ),
        Tool(
            name="loopdesk.run_local_command",
            description="Run a local command in the workspace and record the result as a tool event.",
            inputSchema={
                "type": "object",
                "properties": {"argv": {"type": "array", "items": {"type": "string"}}, "work_id": {"type": "string"}},
                "required": ["argv"],
            },
        ),
    ]


def _build_server() -> Server:
    server = Server("loopdesk-workspace")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return _build_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, object]) -> list[TextContent]:
        if name == "loopdesk.get_context_pack":
            payload = LoopWorkspaceService.from_root(_workspace_root()).get_context_pack()
            return [TextContent(type="text", text=serialize_json_payload(payload))]
        if name == "loopdesk.list_templates":
            LoopWorkspaceService.from_root(_workspace_root())
            payload = {
                "templates": [
                    {
                        "id": template.id,
                        "name": template.name,
                        "description": template.description,
                        "roles": template.roles,
                    }
                    for template in list_personal_templates()
                ]
            }
            return [TextContent(type="text", text=serialize_json_payload(payload))]
        if name == "loopdesk.read_template":
            template = load_personal_template(str(arguments.get("template_id", "")))
            payload = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "loop_steps": template.loop_steps,
                "goal_steps": template.goal_steps,
                "roles": template.roles,
            }
            return [TextContent(type="text", text=serialize_json_payload(payload))]
        if name == "loopdesk.run_local_command":
            from loopdesk.loop_workspace.cli_bridge import LocalCliBridge

            service = LoopWorkspaceService.from_root(_workspace_root())
            bridge = LocalCliBridge(service.repository, artifact_dir=service.layout.artifacts_dir)
            payload = bridge.run("mcp", list(arguments.get("argv", [])), work_id=str(arguments.get("work_id") or ""))
            return [TextContent(type="text", text=serialize_json_payload(payload))]
        raise ValueError(f"Unknown tool: {name}")

    return server


def _run_stdio_streams(read_stream, write_stream) -> None:
    server = _build_server()
    asyncio.run(server.run(read_stream, write_stream, server.create_initialization_options()))


async def _run_stdio() -> None:
    from mcp.server.stdio import stdio_server

    server = _build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
