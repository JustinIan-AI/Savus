"""Direct-run focused validation for LoopDesk v0.2 channel adapter.

This script exercises the same focused areas as the pytest gate without
depending on pytest collection/execution, which is currently blocked in
this environment.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from loopdesk.channels.command_registry import DEFAULT_COMMAND_REGISTRY, build_channel_rpc_context
from loopdesk.channels.dingtalk import DingTalkChannel, DingTalkChannelConfig
from loopdesk.channels.feishu import FeishuChannel, FeishuChannelConfig
from loopdesk.channels.slack import SlackChannel
from loopdesk.channels.types import OutgoingMessage
from loopdesk.channels.wecom import WeComChannel, WeComChannelConfig
from loopdesk.gateway.config import GatewayConfig, ChannelsConfig, DingTalkChannelEntry, FeishuChannelEntry, SlackChannelEntry, WeComChannelEntry
from loopdesk.gateway.protocol import make_ok_res
from loopdesk.gateway.routing import build_channel_route_envelope
from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.gateway.scopes import resolve_required_scope
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.channels.types import IncomingMessage


def _direct_fail(message: str) -> None:
    raise AssertionError(message)


def _run(coro):
    try:
        return asyncio.get_running_loop().run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def test_core_foundation() -> None:
    if resolve_required_scope("loop_workspace.current") != "operator.read":
        _direct_fail("scope classification mismatch")


def test_notification_formatter() -> None:
    message = OutgoingMessage(
        content="Cost alert: spend=6.0, budget_cap_usd=5.0.",
        reply_to="session-1",
        metadata={"command": "cost", "payload": {"spend_usd": 6.0, "budget_cap_usd": 5.0, "status": "exceeded"}},
    )
    if not message.content.startswith("Cost alert:"):
        _direct_fail("cost alert prefix mismatch")
    if "spend=6.0" not in message.content or "budget=5.0" not in message.content:
        _direct_fail("cost alert values missing")
    if len(message.content) > 120:
        _direct_fail("cost alert length exceeded")


def test_feishu_adapter() -> None:
    channel = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret"))
    if channel.capability_profile.transports != ("websocket",):
        _direct_fail("feishu transport mismatch")
    reply = channel.parse_event({
        "header": {"event_id": "evt_1", "event_type": "im.message.receive_v1"},
        "event": {"message": {"content": '{"text":"/current"}', "message_id": "om_123", "thread_id": "om_456", "chat_id": "oc_123"}},
    })
    if not isinstance(reply, IncomingMessage):
        _direct_fail("feishu parse_event should return IncomingMessage")
    if reply.metadata.get("native_thread_id") != "om_456":
        _direct_fail("feishu thread_id missing")
    if reply.metadata.get("reply_target_id") != "om_123":
        _direct_fail("feishu reply_target_id missing")
    config = GatewayConfig(channels=ChannelsConfig(channels=[FeishuChannelEntry.model_validate({
        "type": "feishu", "name": "feishu-work", "app_id": "app", "app_secret": "secret", "enabled": False,
    })]))
    if config.channels.channels[0].enabled is not False:
        _direct_fail("feishu disabled config mismatch")


def test_slack_adapter() -> None:
    channel = SlackChannel(token="xoxb-secret", slack_channel_id="C-default", connection_mode="socket")
    if channel.capability_profile.transports != ("websocket",):
        _direct_fail("slack transport mismatch")
    reply = channel.parse_event({
        "type": "message",
        "channel": "C1",
        "user": "U1",
        "ts": "1700000000.000200",
        "thread_ts": "1700000000.000100",
        "text": "/current",
    })
    if not isinstance(reply, IncomingMessage):
        _direct_fail("slack parse_event should return IncomingMessage")
    if reply.metadata.get("thread_ts") != "1700000000.000100":
        _direct_fail("slack thread_ts missing")
    config = GatewayConfig(channels=ChannelsConfig(channels=[SlackChannelEntry.model_validate({
        "type": "slack", "name": "slack-main", "connection_mode": "socket", "token": "xoxb-secret", "app_token": "xapp-secret", "enabled": False,
    })]))
    if config.channels.channels[0].enabled is not False:
        _direct_fail("slack disabled config mismatch")


def test_dingtalk_adapter() -> None:
    channel = DingTalkChannel(DingTalkChannelConfig())
    if "websocket" not in channel.capability_profile.transports:
        _direct_fail("dingtalk transport mismatch")
    config = GatewayConfig(channels=ChannelsConfig(channels=[DingTalkChannelEntry.model_validate({
        "type": "dingtalk", "name": "dingtalk-personal", "client_id": "client", "client_secret": "secret", "enabled": False,
    })]))
    if config.channels.channels[0].enabled is not False:
        _direct_fail("dingtalk disabled config mismatch")


def test_wecom_adapter() -> None:
    channel = WeComChannel(WeComChannelConfig())
    if channel.capability_profile.transports != ("webhook",):
        _direct_fail("wecom transport mismatch")
    config = GatewayConfig(channels=ChannelsConfig(channels=[WeComChannelEntry.model_validate({
        "type": "wecom", "name": "wecom-ops", "corp_id": "corp", "corp_secret": "secret", "agent_id_int": 1000002, "token": "token", "encoding_aes_key": "aes", "public_webhook_reviewed": False, "enabled": True,
    })]))
    if config.channels.channels[0].enabled is not False:
        _direct_fail("wecom review gate mismatch")
    config = GatewayConfig(channels=ChannelsConfig(channels=[WeComChannelEntry.model_validate({
        "type": "wecom", "name": "wecom-ops", "corp_id": "corp", "corp_secret": "secret", "agent_id_int": 1000002, "token": "token", "encoding_aes_key": "aes", "public_webhook_reviewed": True, "enabled": True,
    })]))
    if config.channels.channels[0].enabled is not True:
        _direct_fail("wecom approved gate mismatch")


def test_rpc_channels_status() -> None:
    ctx = type("Ctx", (), {"principal": type("P", (), {"role": "operator", "scopes": frozenset(["operator.admin"]), "is_owner": True, "authenticated": True})(), "config": GatewayConfig(channels=ChannelsConfig(channels=[SlackChannelEntry(name="slack-main", type="slack", token="xoxb-secret", app_token="xapp-secret", enabled=False)]))})()
    payload = _run(get_dispatcher().dispatch("r1", "channels.status", {}, ctx)).payload
    if payload is None or payload["channels"][0]["status"] != "disabled":
        _direct_fail("channels.status disabled payload mismatch")


def test_loop_workspace_routes() -> None:
    root = Path("/tmp") / "loopdesk-channel-rpc-check"
    root.mkdir(parents=True, exist_ok=True)
    payload = get_dispatcher().handle("loop_workspace.get", {"root": str(root)}, type("Ctx", (), {"principal": type("P", (), {"role": "operator", "scopes": frozenset(["operator.admin"]), "is_owner": True, "authenticated": True})(), "config": GatewayConfig()})())
    if payload.get("workspace_root") != str(root):
        _direct_fail("loop_workspace.get root mismatch")
    if "run_log" not in payload or "approvals" not in payload:
        _direct_fail("loop_workspace.get missing fields")


class _FakeDispatcher:
    async def dispatch(self, req_id, method, params, ctx):
        return make_ok_res(req_id, {"status": "completed"})


def test_hardening_primitives() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="u1", channel_id="c1", content="/current"),
        session_key="agent:main:slack:u1",
        session_prefix="slack",
    )
    ctx = build_channel_rpc_context(
        envelope,
        gateway_config=GatewayConfig(),
        channel_admin_senders={"slack": ["u1"]},
    )
    fake = _FakeDispatcher()
    first = _run(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=fake, context_factory=lambda _envelope: ctx))
    second = _run(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=fake, context_factory=lambda _envelope: ctx))
    third = _run(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/current", rpc_dispatcher=fake, context_factory=lambda _envelope: ctx))
    if first is None or first.content != "/current completed":
        _direct_fail("hardening first response mismatch")
    if second is None or second.content != "/current completed":
        _direct_fail("hardening second response mismatch")
    if third is None or not third.content.startswith("Too many /current attempts."):
        _direct_fail("hardening throttle mismatch")


def main() -> int:
    checks = [
        test_core_foundation,
        test_notification_formatter,
        test_feishu_adapter,
        test_slack_adapter,
        test_dingtalk_adapter,
        test_wecom_adapter,
        test_rpc_channels_status,
        test_loop_workspace_routes,
        test_hardening_primitives,
    ]
    failures = []
    for check in checks:
        try:
            check()
            print(f"PASS {check.__name__}")
        except AssertionError as exc:
            failures.append((check.__name__, str(exc)))
            print(f"FAIL {check.__name__}: {exc}")
    if failures:
        print(f"\n{len(failures)} focused check(s) failed.")
        return 1
    print("\nAll direct focused checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
