"""RPC endpoint tests for LoopDesk v0.2 local channel inspection."""

from __future__ import annotations

import asyncio
from pathlib import Path
import tempfile

from loopdesk.gateway.rpc import RpcContext, get_dispatcher
from loopdesk.gateway.auth import Principal
from loopdesk.gateway.config import GatewayConfig, ChannelsConfig, SlackChannelEntry


def _ctx() -> RpcContext:
    return RpcContext(
        conn_id="t",
        principal=Principal(
            role="operator",
            scopes=frozenset({"operator.admin"}),
            is_owner=True,
            authenticated=True,
        ),
    )


def _dispatch(method: str, params: dict[str, object], ctx: RpcContext) -> dict[str, object]:
    async def _run() -> dict[str, object]:
        response = await get_dispatcher().dispatch("r1", method, params, ctx)
        payload = response.payload if hasattr(response, "payload") else response
        if isinstance(payload, dict) and payload.get("ok") is None and "error" in payload:
            raise RuntimeError(payload.get("error", payload))
        return payload

    return asyncio.run(_run())


def test_channels_status_includes_disabled_loop_workspace_status() -> None:
    ctx = _ctx()
    ctx.config = GatewayConfig(
        channels=ChannelsConfig(
            channels=[SlackChannelEntry(name="slack-main", type="slack", token="xoxb-secret", app_token="xapp-secret", enabled=False)],
        )
    )

    payload = _dispatch("channels.status", {}, ctx)
    assert payload["channels"][0]["enabled"] is False
    assert payload["channels"][0]["status"] == "disabled"


def test_loop_workspace_channel_route_exposes_workspace_state() -> None:
    root = Path(tempfile.mkdtemp(prefix="loopdesk-channel-rpc-check")).resolve()
    payload = _dispatch("loop_workspace.get", {"root": str(root)}, _ctx())

    assert payload["workspace_root"] == str(root)
    assert "run_log" in payload
    assert "approvals" in payload
