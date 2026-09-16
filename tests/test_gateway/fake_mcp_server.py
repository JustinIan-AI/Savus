"""Minimal fake MCP server for adapter tests."""

from __future__ import annotations

import json
import sys

TOOLS = [
    {"name": "echo", "description": "Echo input", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}}},
]


def main() -> None:
    for line in sys.stdin:
        payload = json.loads(line)
        method = payload.get("method")
        request_id = payload.get("id")
        if method == "initialize":
            response = {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "fake-mcp", "version": "0.1.0"}}}
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            name = payload.get("params", {}).get("name")
            arguments = payload.get("params", {}).get("arguments", {})
            response = {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps({"name": name, "arguments": arguments})}]}}
        else:
            response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
