"""Inbound MCP server bridge for LoopDesk.

This package exposes LoopDesk sessions to external MCP clients. It is
intentionally separate from :mod:`loopdesk.mcp`, which is the outbound MCP
client integration used to import tools from external MCP servers.
"""

from loopdesk.mcp_server.bridge import LoopDeskMCPBridge
from loopdesk.mcp_server.server import create_mcp_server

__all__ = ["LoopDeskMCPBridge", "create_mcp_server"]
