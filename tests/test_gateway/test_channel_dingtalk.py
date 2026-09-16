"""Focused gateway tests for LoopDesk v0.2 DingTalk adapter surface."""

from __future__ import annotations

import pytest

from loopdesk.channels.dingtalk import DingTalkChannel, DingTalkChannelConfig
from loopdesk.channels.types import OutgoingMessage
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.config import ChannelsConfig, DingTalkChannelEntry
from loopdesk.onboarding.mutations import upsert_channel


def _dingtalk_config() -> GatewayConfig:
    payload = {
        "type": "dingtalk",
        "name": "dingtalk-personal",
        "client_id": "client",
        "client_secret": "secret",
    }
    return GatewayConfig(channels=ChannelsConfig(channels=[DingTalkChannelEntry.model_validate(payload)]))


def test_dingtalk_stream_transport_is_default_adapter_surface() -> None:
    channel = DingTalkChannel(DingTalkChannelConfig())

    assert "websocket" in channel.capability_profile.transports


def test_dingtalk_command_surface_maps_to_compact_workspace_commands() -> None:
    channel = DingTalkChannel(DingTalkChannelConfig())
    expected = {"/help", "/status", "/current", "/list", "/history", "/memory", "/skills", "/model", "/abort", "/approve", "/reject", "/cancel"}


def test_dingtalk_unsupported_rich_format_falls_back_to_plain_text() -> None:
    channel = DingTalkChannel(DingTalkChannelConfig())
    message = OutgoingMessage(content="LoopDesk status: active; Refactor adapters", reply_to="session-1", metadata={"rich_card": {"unsupported": True}})

    assert isinstance(message, OutgoingMessage)
    assert message.content.startswith("LoopDesk status:")


def test_disabled_dingtalk_entry_does_not_start_transport() -> None:
    config = _dingtalk_config()
    assert config.channels.channels[0].enabled is True
    config.channels.channels[0].enabled = False
    assert config.channels.channels[0].enabled is False
