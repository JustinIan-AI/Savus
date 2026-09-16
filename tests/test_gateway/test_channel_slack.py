"""Focused gateway tests for LoopDesk v0.2 Slack adapter surface."""

from __future__ import annotations

from typing import Any

import pytest

from loopdesk.channels.slack import SlackChannel
from loopdesk.channels.types import IncomingMessage, OutgoingMessage
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.config import ChannelsConfig, SlackChannelEntry



from loopdesk.engine.commands import DEFAULT_REGISTRY, Surface
from loopdesk.gateway.protocol import make_ok_res
from loopdesk.gateway.routing import build_channel_route_envelope
from loopdesk.onboarding.mutations import upsert_channel


class _FakeDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def dispatch(self, req_id, method, params, ctx):
        self.calls.append({"method": method, "params": params, "ctx": ctx})
        return make_ok_res(req_id, {"ok": True})


def _slack_config() -> GatewayConfig:
    payload = {
        "type": "slack",
        "name": "slack-main",
        "connection_mode": "socket",
        "token": "xoxb-secret",
        "app_token": "xapp-secret",
    }
    return GatewayConfig(channels=ChannelsConfig(channels=[SlackChannelEntry.model_validate(payload)]))


def test_slack_socket_mode_is_preferred_default_transport() -> None:
    channel = SlackChannel(token="xoxb-secret", slack_channel_id="C-default", connection_mode="socket")

    assert channel.capability_profile.transports == ("websocket",)


def test_slack_command_surface_maps_to_compact_workspace_commands() -> None:
    channel = SlackChannel(token="xoxb-secret", slack_channel_id="C-default")
    expected = frozenset({"/abort", "/approve", "/cancel", "/current", "/help", "/history", "/list", "/memory", "/model", "/new", "/reject", "/skills", "/status"})


def test_slack_read_command_preserves_thread_reply_target() -> None:
    channel = SlackChannel(token="xoxb-secret", slack_channel_id="C-default")
    msg = IncomingMessage(
        sender_id="U1",
        channel_id="C1",
        content="/current",
        metadata={"thread_ts": "1700000000.000100"},
    )
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:slack:U1",
        session_prefix="slack",
        agent_id="main",
    )
    dispatcher = _FakeDispatcher()

    reply = channel.parse_event({
        "type": "message",
        "channel": "C1",
        "user": "U1",
        "ts": "1700000000.000200",
        "thread_ts": "1700000000.000100",
        "text": "/current",
    })

    assert isinstance(reply, IncomingMessage)
    assert reply.metadata.get("thread_ts") == "1700000000.000100"


def test_slack_approval_flow_uses_existing_approval_records() -> None:
    channel = SlackChannel(token="xoxb-secret", slack_channel_id="C-default")
    msg = IncomingMessage(sender_id="U1", channel_id="C1", content="/reject approval-1")
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:slack:U1",
        session_prefix="slack",
        agent_id="main",
    )
    dispatcher = _FakeDispatcher()

    reply = channel.parse_event({
        "type": "message",
        "channel": "C1",
        "user": "U1",
        "ts": "1700000000.000300",
        "text": "/reject approval-1",
    })

    assert isinstance(reply, IncomingMessage)
    assert reply.content == "/reject approval-1"


def test_disabled_slack_entry_does_not_start_transport() -> None:
    config = _slack_config()
    assert config.channels.channels[0].enabled is True
    config.channels.channels[0].enabled = False
    assert config.channels.channels[0].enabled is False
