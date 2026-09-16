"""Minimal MCP stdio client for LoopDesk adapters."""

from __future__ import annotations

import json
from typing import Any


class McpClient:
    def __init__(self) -> None:
        self._request_id = 0
        self._process = None

    def connect(self, command: str, args: list[str] | None = None) -> None:
        import shutil
        import subprocess

        if shutil.which(command) is None:
            raise FileNotFoundError(command)
        self._process = subprocess.Popen(
            [command, *(args or [])],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def list_tools(self) -> list[dict[str, Any]]:
        response = self._call("tools/list", {})
        return response.get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._call("tools/call", {"name": name, "arguments": arguments or {}})

    def disconnect(self) -> None:
        if self._process is not None:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None

    def _call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._process is None:
            raise RuntimeError("MCP client is not connected")
        self._request_id += 1
        payload = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        line = json.dumps(payload) + "\n"
        self._process.stdin.write(line)
        self._process.stdin.flush()
        raw = self._process.stdout.readline()
        if not raw:
            raise RuntimeError("MCP server closed the connection")
        response = json.loads(raw)
        if "error" in response:
            raise RuntimeError(response["error"])
        return response.get("result", {})
