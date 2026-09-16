"""FastMCP server factory for exposing LoopDesk session workflows."""

from __future__ import annotations

from typing import Any

from loopdesk.mcp_server.bridge import LoopDeskMCPBridge


def create_mcp_server(
    bridge: LoopDeskMCPBridge | None = None,
    *,
    name: str = "LoopDesk",
    fastmcp_cls: type[Any] | None = None,
) -> Any:
    """Create a FastMCP app with product-oriented LoopDesk tools/resources."""

    if fastmcp_cls is None:
        try:
            from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised through CLI behavior.
            raise RuntimeError(
                "The MCP server requires the optional dependency: install loopdesk[mcp]."
            ) from exc
        fastmcp_cls = FastMCP

    bridge = bridge or LoopDeskMCPBridge()
    mcp = fastmcp_cls(name, json_response=True)

    @mcp.tool(name="conversations_list")
    async def conversations_list(limit: int = 50) -> dict[str, Any]:
        """List LoopDesk sessions visible to the connected gateway principal."""

        return await bridge.conversations_list(limit=limit)

    @mcp.tool(name="session_resolve")
    async def session_resolve(key: str) -> dict[str, Any]:
        """Resolve a session key or identifier to LoopDesk session metadata."""

        return await bridge.session_resolve(key)

    @mcp.tool(name="messages_read")
    async def messages_read(key: str, limit: int = 1000) -> dict[str, Any]:
        """Read persisted messages for an LoopDesk session."""

        return await bridge.messages_read(key, limit=limit)

    @mcp.tool(name="messages_send")
    async def messages_send(key: str, message: str, intent: str = "continue") -> dict[str, Any]:
        """Send a user message to an existing LoopDesk session."""

        return await bridge.messages_send(key, message, intent=intent)

    @mcp.tool(name="events_wait")
    async def events_wait(
        key: str,
        since_stream_seq: int | None = None,
        timeout_ms: int = 30_000,
        max_events: int = 100,
        terminal_only: bool = False,
    ) -> dict[str, Any]:
        """Wait for live or replayed gateway events for an LoopDesk session."""

        return await bridge.events_wait(
            key,
            since_stream_seq=since_stream_seq,
            timeout_ms=timeout_ms,
            max_events=max_events,
            terminal_only=terminal_only,
        )

    @mcp.tool(name="transcript_export")
    async def transcript_export(key: str, limit: int = 1000) -> str:
        """Export a session transcript as JSONL with standard tool evidence events."""

        return await bridge.transcript_jsonl(key, limit=limit)

    @mcp.resource("loopdesk://sessions")
    async def sessions_resource() -> dict[str, Any]:
        return await bridge.conversations_list()

    @mcp.resource("loopdesk://sessions/{key}")
    async def session_resource(key: str) -> dict[str, Any]:
        return await bridge.session_resolve(key)

    @mcp.resource("loopdesk://sessions/{key}/messages")
    async def session_messages_resource(key: str) -> dict[str, Any]:
        return await bridge.messages_read(key)

    @mcp.resource("loopdesk://sessions/{key}/transcript.jsonl")
    async def session_transcript_resource(key: str) -> str:
        return await bridge.transcript_jsonl(key)

    return mcp
