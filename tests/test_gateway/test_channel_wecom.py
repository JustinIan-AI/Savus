"""Focused gateway tests for LoopDesk v0.2 WeCom adapter review gate."""

from __future__ import annotations

import pytest

from loopdesk.channels.wecom import WeComChannel, WeComChannelConfig



from loopdesk.engine.commands import DEFAULT_REGISTRY, Surface
from loopdesk.channels.types import OutgoingMessage
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.config import ChannelsConfig, WeComChannelEntry
from loopdesk.onboarding.mutations import upsert_channel


def _wecom_config(**payload: object) -> GatewayConfig:
    payload = {
        "type": "wecom",
        "name": "wecom-ops",
        "corp_id": "corp",
        "corp_secret": "secret",
        "agent_id_int": 1000002,
        "token": "token",
        "encoding_aes_key": "aes",
        **payload,
    }
    return GatewayConfig(channels=ChannelsConfig(channels=[WeComChannelEntry.model_validate(payload)]))


def test_wecom_public_webhook_requires_review_gate() -> None:
    config = _wecom_config(public_webhook_reviewed=False)
    assert config.channels.channels[0].enabled is False


def test_wecom_approved_review_gate_can_be_enabled() -> None:
    config = _wecom_config(public_webhook_reviewed=True, enabled=True)
    assert config.channels.channels[0].enabled is True


def test_wecom_command_surface_maps_to_compact_workspace_commands() -> None:
    channel = WeComChannel(WeComChannelConfig())
    expected = frozenset({"/approve", "/cancel", "/current", "/help", "/list", "/memory", "/model", "/new", "/reject", "/skills", "/status"})


def test_wecom_compact_error_template_stays_readable() -> None:
    message = OutgoingMessage(content="WeCom cost alert: budget review needed.", reply_to="chat-1", metadata={"command": "cost"})

    assert isinstance(message, OutgoingMessage)
    assert message.content.startswith("WeCom cost alert:")
    assert len(message.content) <= 120
