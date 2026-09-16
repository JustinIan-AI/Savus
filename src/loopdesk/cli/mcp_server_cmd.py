"""CLI commands for running LoopDesk as an inbound MCP server."""

from __future__ import annotations

import typer

from loopdesk.cli.url_utils import normalize_gateway_url

app = typer.Typer(help="Run the LoopDesk MCP server bridge.")


@app.command("run")
def run_mcp_server(
    gateway_url: str = typer.Option(
        "ws://localhost:18791/ws",
        "--gateway",
        envvar="LOOPDESK_GATEWAY_URL",
        help="LoopDesk gateway URL to bridge to.",
    ),
) -> None:
    """Run a stdio MCP server exposing LoopDesk session workflows."""

    from loopdesk.mcp_server.bridge import LoopDeskMCPBridge
    from loopdesk.mcp_server.server import create_mcp_server

    bridge = LoopDeskMCPBridge(gateway_url=normalize_gateway_url(gateway_url))
    try:
        mcp = create_mcp_server(bridge)
    except RuntimeError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc

    mcp.run(transport="stdio")
