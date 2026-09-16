"""Focused gateway tests for LoopDesk v0.2 channel hardening behavior."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from loopdesk.channels.types import OutgoingMessage
from loopdesk.channels.command_registry import build_channel_rpc_context, DEFAULT_COMMAND_REGISTRY
from loopdesk.gateway.auth import Principal
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.protocol import make_error_res, make_ok_res
from loopdesk.gateway.routing import build_channel_route_envelope


class _RateLimiter:
    def __init__(self) -> None:
        self.attempts = 0
        self.rejected = 0

    async def allow(self, key: str) -> bool:
        self.attempts += 1
        if self.attempts <= 2:
            return True
        self.rejected += 1
        return False


class _AuditLog:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def record(self, record: dict[str, Any]) -> None:
        self.records.append(record)


class _ChannelService:
    def __init__(self, *, rate_limiter: _RateLimiter, audit_log: _AuditLog) -> None:
        self.rate_limiter = rate_limiter
        self.audit_log = audit_log
        self.cancelled_immediately = False

    async def handle_command(self, sender_key: str, command: str) -> tuple[str, OutgoingMessage | None]:
        if not await self.rate_limiter.allow(sender_key):
            self.audit_log.record({"sender_key": sender_key, "command": command, "result": "throttled"})
            return "throttled", OutgoingMessage(content=f"Too many {command} attempts.", reply_to="session-1")

        self.audit_log.record({"sender_key": sender_key, "command": command, "result": "accepted"})
        if command == "/cancel":
            self.cancelled_immediately = True
            return "cancelled", OutgoingMessage(content="Cancelled.", reply_to="session-1")

        return "completed", OutgoingMessage(content=f"{command} completed.", reply_to="session-1")


class _FakeDispatcher:
    def __init__(self, *, error_code: str = "INTERNAL_ERROR") -> None:
        self.error_code = error_code

    async def dispatch(self, req_id, method, params, ctx):
        if self.error_code == "UNAUTHORIZED":
            return make_error_res(req_id, "UNAUTHORIZED", "sender not in admin allowlist")
        if method == "loop_workspace.cost.set_budget":
            return make_ok_res(req_id, {"status": "completed"})
        if method == "sessions.abort":
            return make_ok_res(req_id, {"status": "completed"})
        return make_ok_res(req_id, {"ok": True})


def test_repeated_channel_commands_are_throttled_and_logged() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="u1", channel_id="c1", content="/current"),
        session_key="agent:main:slack:u1",
        session_prefix="slack",
    )
    service = _ChannelService(rate_limiter=_RateLimiter(), audit_log=_AuditLog())

    ctx = build_channel_rpc_context(
        envelope,
        gateway_config=GatewayConfig(),
        channel_admin_senders={"slack": ["u1"]},
    )

    first = asyncio.get_event_loop().run_until_complete(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: ctx))
    second = asyncio.get_event_loop().run_until_complete(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: ctx))
    third = asyncio.get_event_loop().run_until_complete(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: ctx))
    fourth = asyncio.get_event_loop().run_until_complete(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: ctx))

    assert first is not None and first.content == "/current completed"
    assert second is not None and second.content == "/current completed"
    assert third is not None and third.content.startswith("Too many /current attempts.")
    assert fourth is not None and fourth.content.startswith("Too many /current attempts.")
    assert [record["result"] for record in service.audit_log.records] == ["accepted", "accepted", "throttled", "throttled"]


def test_budget_cap_exceeded_sends_compact_cost_alert() -> None:
    service = _ChannelService(rate_limiter=_RateLimiter(), audit_log=_AuditLog())
    payload = {
        "spend_usd": 6.0,
        "budget_cap_usd": 5.0,
        "status": "exceeded",
    }
    message = ChannelNotificationFormatter.format_cost_alert(payload)

    assert message.content.startswith("Cost alert:")
    assert "spend=6.0" in message.content
    assert "budget=5.0" in message.content
    assert len(message.content) <= 120


def test_cancel_returns_immediate_status_without_blocking_im_session() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="u1", channel_id="c1", content="/cancel"),
        session_key="agent:main:slack:u1",
        session_prefix="slack",
    )
    ctx = build_channel_rpc_context(
        envelope,
        gateway_config=GatewayConfig(),
        channel_admin_senders={"slack": ["u1"]},
    )
    service = _ChannelService(rate_limiter=_RateLimiter(), audit_log=_AuditLog())

    reply = asyncio.get_event_loop().run_until_complete(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/cancel", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: ctx))

    assert reply is not None
    assert reply.content == "Cancelled."
    assert service.cancelled_immediately is True
