"""Thin stdio script for LoopDesk workspace MCP tools."""

from __future__ import annotations

import sys

from loopdesk.loop_workspace.mcp import main

if __name__ == "__main__":
    raise SystemExit(main())
