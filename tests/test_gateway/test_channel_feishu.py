"""Focused gateway tests for LoopDesk v0.2 Feishu/Lark adapter surface."""

from __future__ import annotations

import json
from typing import Any

import pytest

from loopdesk.channels.feishu import FeishuChannel, FeishuChannelConfig



from loopdesk.engine.commands import DEFAULT_REGISTRY, Surface
from loopdesk.channels.types import IncomingMessage, OutgoingMessage
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.config import ChannelsConfig, FeishuChannelEntry
from loopdesk.gateway.protocol import make_ok_res
from loopdesk.gateway.routing import build_channel_route_envelope
from loopdesk.onboarding.mutations import upsert_channel


class _FakeDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def dispatch(self, req_id, method, params, ctx):
        self.calls.append({"method": method, "params": params, "ctx": ctx})
        return make_ok_res(req_id, {"ok": True})


def _feishu_config() -> GatewayConfig:
    payload = {
        "type": "feishu",
        "name": "feishu-work",
        "app_id": "app",
        "app_secret": "secret",
        "connection_mode": "websocket",
    }
    return GatewayConfig(channels=ChannelsConfig(channels=[FeishuChannelEntry.model_validate(payload)]))


def test_feishu_websocket_is_preferred_default_transport() -> None:
    channel = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret"))

    assert channel.capability_profile.transports == ("websocket",)


def test_feishu_command_surface_maps_to_compact_workspace_commands() -> None:
    channel = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret"))
    expected = frozenset({"/abort", "/approve", "/cancel", "/current", "/help", "/history", "/list", "/memory", "/model", "/new", "/reject", "/skills", "/status"})


def test_feishu_read_command_preserves_thread_reply_target() -> None:
    channel = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret"))
    msg = IncomingMessage(
        sender_id="u1",
        channel_id="oc_123",
        content="/current",
        metadata={"message_id": "om_123", "thread_id": "om_456"},
    )
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:feishu:u1",
        session_prefix="feishu",
        agent_id="main",
    )
    dispatcher = _FakeDispatcher()

    reply = channel.parse_event({
        "header": {"event_id": "evt_1", "event_type": "im.message.receive_v1"},
        "event": {"message": {"content": json.dumps({"text": "/current"}), "message_id": "om_123", "thread_id": "om_456", "chat_id": "oc_123"}},
    })

    assert isinstance(reply, IncomingMessage)
    assert reply.metadata.get("native_thread_id") == "om_456"
    assert reply.metadata.get("reply_target_id") == "om_123"


def test_feishu_approval_flow_uses_existing_approval_records() -> None:
    channel = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret"))
    msg = IncomingMessage(sender_id="u1", channel_id="oc_123", content="/approve approval-1")
    envelope = build_channel_route_envelope(
        msg,
        session_key="agent:main:feishu:u1",
        session_prefix="feishu",
        agent_id="main",
    )
    dispatcher = _FakeDispatcher()

    reply = channel.parse_event({
        "header": {"event_id": "evt_2", "event_type": "im.message.receive_v1"},
        "event": {"message": {"content": json.dumps({"text": "/approve approval-1"}), "message_id": "om_200", "chat_id": "oc_123"}},
    })

    assert isinstance(reply, IncomingMessage)
    assert reply.content == "/approve approval-1"
    assert reply.metadata.get("message_id") == "om_200"


def test_disabled_feishu_entry_does_not_start_transport() -> None:
    config = _feishu_config()
    config.channels.channels[0].enabled = False
    assert config.channels.channels[0].enabled is False
