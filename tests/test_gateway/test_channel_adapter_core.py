"""Focused gateway tests for LoopDesk v0.2 channel core behavior."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from loopdesk.channels.command_registry import build_channel_rpc_context
from loopdesk.channels.manager import ChannelManager
from loopdesk.channels.types import ChannelHealth, IncomingMessage
from loopdesk.gateway.auth import Principal
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.protocol import make_error_res, make_ok_res
from loopdesk.channels.command_registry import DEFAULT_COMMAND_REGISTRY
from loopdesk.gateway.routing import SourceKind, build_channel_route_envelope
from loopdesk.gateway.scopes import resolve_required_scope
from loopdesk.onboarding.mutations import upsert_channel


def _gateway_config(**channel_payload: object) -> GatewayConfig:
    channel_type = str(channel_payload.get("type", "slack"))
    defaults: dict[str, object] = {"name": "work", "type": channel_type}
    if channel_type == "slack":
        defaults.setdefault("token", "xoxb-test")
        defaults.setdefault("signing_secret", "secret")
        defaults.setdefault("connection_mode", "webhook")
    elif channel_type == "feishu":
        defaults.setdefault("app_id", "app")
        defaults.setdefault("app_secret", "secret")
        defaults.setdefault("connection_mode", "websocket")
    elif channel_type == "dingtalk":
        defaults.setdefault("client_id", "client")
        defaults.setdefault("client_secret", "secret")
    elif channel_type == "wecom":
        defaults.setdefault("corp_id", "corp")
        defaults.setdefault("corp_secret", "secret")
        defaults.setdefault("token", "token")
        defaults.setdefault("encoding_aes_key", "aes")
    return upsert_channel(GatewayConfig(), entry_payload={**defaults, **channel_payload}).config


def test_channel_rpc_context_gives_admin_sender_write_scopes() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="U1", channel_id="C1", content=""),
        session_key="agent:main:slack:U1",
        session_prefix="slack",
    )
    ctx = build_channel_rpc_context(
        envelope,
        gateway_config=_gateway_config(),
        channel_admin_senders={"slack": ["U1"]},
    )

    assert ctx.principal.role == "operator"
    assert ctx.principal.scopes == frozenset({"operator.read", "operator.write"})
    assert ctx.principal.is_owner is False
    assert ctx.principal.authenticated is True


def test_channel_rpc_context_treats_non_admin_sender_as_viewer() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="U2", channel_id="C1", content=""),
        session_key="agent:main:slack:U2",
        session_prefix="slack",
    )
    ctx = build_channel_rpc_context(
        envelope,
        gateway_config=_gateway_config(),
        channel_admin_senders={"slack": ["U1"]},
    )

    assert ctx.principal.role == "viewer"
    assert ctx.principal.scopes == frozenset()


def test_disabled_channel_entry_is_skipped_by_manager() -> None:
    class _FakeChannel:
        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        async def health_check(self) -> ChannelHealth:
            return ChannelHealth(connected=False)

        def create_route(self, path: str | None = None):
            from starlette.routing import Route
            return Route(path or "/events", endpoint=lambda request: None)

        async def receive(self) -> IncomingMessage:
            raise RuntimeError("no test events")

    manager = ChannelManager(
        {
            "enabled": _FakeChannel(),
        },
        _turn_runner=object(),
        _session_manager=object(),
        _channel_types={"enabled": "slack"},
    )

    assert manager.get("enabled") is not None
    assert manager.get("disabled") is None


def test_unknown_channel_command_is_rejected_before_workspace_action() -> None:
    msg = IncomingMessage(sender_id="u1", channel_id="c1", content="/unknown")
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:slack:u1",
        session_prefix="slack",
    )

    reply = asyncio.get_event_loop().run_until_complete(
        DEFAULT_COMMAND_REGISTRY.dispatch(
            envelope=envelope,
            message_content="/unknown",
            rpc_dispatcher=_FakeDispatcher(),
            context_factory=lambda _envelope: object(),
        )
    )

    assert reply is None


def test_blocked_write_command_returns_denied_status_with_metadata() -> None:
    msg = IncomingMessage(sender_id="u1", channel_id="c1", content="/new")
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:slack:u1",
        session_prefix="slack",
    )

    reply = asyncio.get_event_loop().run_until_complete(
        DEFAULT_COMMAND_REGISTRY.dispatch(
            envelope=envelope,
            message_content="/new",
            rpc_dispatcher=_FakeDispatcher(error_code="UNAUTHORIZED"),
            context_factory=lambda _envelope: object(),
        )
    )

    assert reply is not None
    assert reply.content.startswith("/new denied")
    assert reply.metadata["command"] == "new"
    assert reply.metadata["denied"] is True


@pytest.mark.parametrize(
    "method,expected",
    [
        ("channels.status", "operator.read"),
        ("channels.restart", "operator.admin"),
        ("loop_workspace.get", "operator.read"),
        ("loop_workspace.record_work_item", "operator.write"),
        ("loop_workspace.adapter.call_tool", "operator.write"),
    ],
)
def test_v0_2_scope_table_classifies_channel_and_workspace_methods(method: str, expected: str) -> None:
    assert resolve_required_scope(method) == expected


def test_channel_status_reports_disabled_adapter_without_corrupting_local_behavior() -> None:
    class _FakeHealth:
        connected = False

    class _FakeManager:
        _channel_types = {}

        async def health(self):
            return {}

        def get(self, name: str):
            return None

    ctx = _read_ctx()
    ctx.channel_manager = _FakeManager()
    ctx.config = _gateway_config(enabled=False)

    rpc_res = _run_sync(
        __import__("loopdesk.gateway.rpc_channels", fromlist=["_handle_channels_status"])._handle_channels_status({}, ctx)
    )

    assert rpc_res["channels"] == [
        {
            "name": "work",
            "connected": False,
            "status": "disabled",
            "bot_user_id": None,
            "connected_since": None,
            "restart_attempts": 0,
            "type": "slack",
            "enabled": False,
            "configured": True,
            "capabilities": [],
            "capability_profile": None,
            "platform_manifest": None,
            "diagnostics": {"network_probe": "not_run"},
        }
    ]


class _FakeDispatcher:
    def __init__(self, *, error_code: str = "INTERNAL_ERROR") -> None:
        self.error_code = error_code

    async def dispatch(self, req_id, method, params, ctx):
        if self.error_code == "UNAUTHORIZED":
            return make_error_res(req_id, "UNAUTHORIZED", "sender not in admin allowlist")
        return make_ok_res(req_id, {"ok": True})


class _RpcContext:
    def __init__(self) -> None:
        self.principal = _FakePrincipal()
        self.config = None
        self.channel_manager = None


class _FakePrincipal:
    role = "operator"
    scopes = frozenset(["operator.admin"])
    is_owner = True
    authenticated = True


def _read_ctx() -> _RpcContext:
    return _RpcContext()


def _run_sync(coro):
    try:
        return asyncio.get_running_loop().run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
