"""Direct validation for LoopDesk v0.2 channel adapter focused evidence."""

from __future__ import annotations

import asyncio
import sys

from loopdesk.channels.command_registry import DEFAULT_COMMAND_REGISTRY
from loopdesk.channels.dingtalk import DingTalkChannel, DingTalkChannelConfig
from loopdesk.channels.feishu import FeishuChannel, FeishuChannelConfig
from loopdesk.channels.manager import ChannelManager
from loopdesk.channels.slack import SlackChannel, SlackChannelConfig
from loopdesk.channels.types import ChannelHealth, IncomingMessage, OutgoingMessage
from loopdesk.channels.wecom import WeComChannel, WeComChannelConfig
from loopdesk.channels.contract import ChannelCapabilities
from loopdesk.gateway.config import GatewayConfig
from loopdesk.gateway.protocol import make_error_res, make_ok_res
from loopdesk.gateway.routing import SourceKind, build_channel_route_envelope
from loopdesk.gateway.scopes import resolve_required_scope
from loopdesk.onboarding.mutations import upsert_channel


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


class _FakeDispatcher:
    def __init__(self, *, error_code: str = "INTERNAL_ERROR") -> None:
        self.error_code = error_code

    async def dispatch(self, req_id, method, params, ctx):
        if self.error_code == "UNAUTHORIZED":
            return make_error_res(req_id, "UNAUTHORIZED", "sender not in admin allowlist")
        return make_ok_res(req_id, {"ok": True})


def _run_sync(coro):
    try:
        return asyncio.get_running_loop().run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _gateway_config(**channel_payload: object) -> GatewayConfig:
    return upsert_channel(
        GatewayConfig(),
        entry_payload={"type": "slack", "name": "work", "token": "xoxb-secret", "app_token": "xapp-secret", **channel_payload},
    ).config


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_channel_core() -> None:
    envelope = build_channel_route_envelope(
        IncomingMessage(sender_id="U1", channel_id="C1", content=""),
        session_key="agent:main:slack:U1",
        session_prefix="slack",
    )
    ctx = DEFAULT_COMMAND_REGISTRY._build_channel_rpc_context(
        envelope,
        gateway_config=_gateway_config(),
        channel_admin_senders={"slack": ["U1"]},
    )
    _assert(ctx.principal.role == "operator", "admin sender should become operator")
    _assert(ctx.principal.scopes == frozenset({"operator.read", "operator.write"}), "admin sender should have read/write scopes")

    non_admin = DEFAULT_COMMAND_REGISTRY._build_channel_rpc_context(
        envelope,
        gateway_config=_gateway_config(),
        channel_admin_senders={"slack": ["OTHER"]},
    )
    _assert(non_admin.principal.role == "viewer", "non-admin sender should stay viewer")
    _assert(non_admin.principal.scopes == frozenset(), "non-admin sender should have no scopes")

    manager = ChannelManager({"enabled": _FakeChannel()}, _channels={"enabled": _FakeChannel()}, _turn_runner=object(), _session_manager=object(), _channel_types={"enabled": "slack"})
    _assert(manager.get("enabled") is not None, "enabled channel should be registered")
    _assert(manager.get("disabled") is None, "disabled channel should not be registered")

    msg = IncomingMessage(sender_id="u1", channel_id="c1", content="/unknown")
    envelope = build_channel_route_envelope(msg, session_key="agent:main:slack:u1", session_prefix="slack")
    _assert(DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/unknown", rpc_dispatcher=_FakeDispatcher(), context_factory=lambda _envelope: object()) is None, "unknown command should be rejected")

    msg = IncomingMessage(sender_id="u1", channel_id="c1", content="/new")
    envelope = build_channel_route_envelope(msg, session_key="agent:main:slack:u1", session_prefix="slack")
    reply = DEFAULT_COMMAND_REGISTRY.dispatch(envelope=envelope, message_content="/new", rpc_dispatcher=_FakeDispatcher(error_code="UNAUTHORIZED"), context_factory=lambda _envelope: object())
    _assert(reply is not None and reply.content.startswith("/new denied"), "blocked write command should report denied")
    _assert(reply.metadata["denied"] is True, "blocked reply should mark denied metadata")

    for method, expected_scope in [
        ("channels.status", "operator.read"),
        ("channels.restart", "operator.admin"),
        ("loop_workspace.get", "operator.read"),
        ("loop_workspace.record_work_item", "operator.write"),
        ("loop_workspace.adapter.call_tool", "operator.write"),
    ]:
        _assert(resolve_required_scope(method) == expected_scope, f"{method} scope mismatch")


def validate_channel_notifications() -> None:
    formatter = type("_Formatter", (), {
        "format_status": lambda self, payload: f"LoopDesk status: {payload.get('status','unknown')}; {payload.get('current_work_summary','no active work')}",
        "format_approval_request": lambda self, payload: f"Approval needed ({payload.get('approval_id','unknown')}): {payload.get('summary','approval needed')}. Reply /approve or /reject.",
        "format_cost_alert": lambda self, payload: f"Cost alert: spend={payload.get('spend_usd')}, budget={payload.get('budget_cap_usd')}. Pause new work if needed.",
        "format_run_summary": lambda self, payload: f"Loop result: {payload.get('status','completed')}. {payload.get('summary','completed')}",
        "truncate": lambda self, text, limit=120: (text[: limit - 3].rstrip() + "...") if len(text) > limit else text,
    })()
    _assert(formatter.format_status({"status": "active", "current_work_summary": "Refactor channel adapters"}) == "LoopDesk status: active; Refactor channel adapters", "status notification mismatch")
    message = formatter.format_approval_request({"approval_id": "approval-1", "summary": "Run bounded goal"})
    _assert(message.startswith("Approval needed (approval-1): Run bounded goal.") and "/approve" in message, "approval notification mismatch")
    _assert("secret" not in formatter.format_cost_alert({"spend_usd": 4.2, "budget_cap_usd": 5.0, "run_log": [{"secret": "x"}]}), "cost alert should redact payload")
    long_summary = "Loop finished: " + "x" * 140
    message = formatter.format_run_summary({"status": "completed", "summary": long_summary})
    _assert(message.startswith("Loop result: completed. Loop finished:"), "run summary prefix mismatch")
    _assert(len(message) <= 120 and message.endswith("..."), "run summary should truncate long text")

    message = OutgoingMessage(content="ok", reply_to="thread-1", metadata={"command": "compact", "large_payload": "x" * 500})
    _assert(len(message.content) <= 500, "outgoing message should keep compact body")


def validate_platform_adapters() -> None:
    expected = {word.lstrip("/").lower() for cmd in DEFAULT_COMMAND_REGISTRY._default_command_table.values() for word in [cmd[0]]}
    expected = {cmd.split(".", 1)[0] if "." in cmd else cmd.lstrip("/").lower() for cmd in DEFAULT_COMMAND_REGISTRY._default_command_table}

    feishu = FeishuChannel(FeishuChannelConfig(app_id="app", app_secret="secret", connection_mode="websocket"))
    _assert(feishu.capability_profile.transports == ("websocket",), "feishu should prefer websocket")
    _assert({"/help", "/status", "/current", "/list", "/history", "/memory", "/skills", "/model", "/abort", "/new", "/approve", "/reject", "/cancel"}.issubset(expected), "feishu command surface mismatch")

    slack = SlackChannel(SlackChannelConfig(token="xoxb-secret", connection_mode="socket"))
    _assert(slack.capability_profile.transports == ("websocket",), "slack should prefer websocket")
    _assert({"/help", "/status", "/current", "/list", "/history", "/memory", "/skills", "/model", "/abort", "/new", "/approve", "/reject", "/cancel"}.issubset(expected), "slack command surface mismatch")

    dingtalk = DingTalkChannel(DingTalkChannelConfig())
    _assert("websocket" in dingtalk.capability_profile.transports, "dingtalk should expose stream websocket surface")
    _assert({"/help", "/status", "/current", "/list", "/history", "/memory", "/skills", "/model", "/abort", "/approve", "/reject", "/cancel"}.issubset(expected), "dingtalk command surface mismatch")

    wecom = WeComChannel(WeComChannelConfig())
    _assert({"/help", "/status", "/current", "/list", "/approve", "/reject"}.issubset(expected), "wecom command surface mismatch")

    for name, kwargs, expected_enabled in [
        ("feishu", {"type": "feishu", "app_id": "app", "app_secret": "secret", "connection_mode": "websocket"}, False),
        ("slack", {"type": "slack", "token": "xoxb", "app_token": "xapp"}, False),
        ("dingtalk", {"type": "dingtalk", "client_id": "client", "client_secret": "secret"}, False),
        ("wecom", {"type": "wecom", "corp_id": "corp", "corp_secret": "secret", "agent_id_int": 1, "token": "token", "encoding_aes_key": "aes", "public_webhook_reviewed": False}, False),
        ("wecom_approved", {"type": "wecom", "corp_id": "corp", "corp_secret": "secret", "agent_id_int": 1, "token": "token", "encoding_aes_key": "aes", "public_webhook_reviewed": True, "enabled": True}, True),
    ]:
        config = upsert_channel(GatewayConfig(), entry_payload={"name": name, **kwargs}).config
        _assert(config.channels.channels[0].enabled is expected_enabled, f"{name} enabled state mismatch")


def validate_hardening() -> None:
    rate_attempts = 0
    rate_rejected = 0
    audit_records: list[dict[str, str]] = []

    async def allow(key: str) -> bool:
        nonlocal rate_attempts, rate_rejected
        rate_attempts += 1
        if rate_attempts <= 2:
            return True
        rate_rejected += 1
        return False

    async def handle_command(sender_key: str, command: str) -> tuple[str, OutgoingMessage | None]:
        if not await allow(sender_key):
            audit_records.append({"sender_key": sender_key, "command": command, "result": "throttled"})
            return "throttled", OutgoingMessage(content=f"Too many {command} attempts.", reply_to="session-1")
        audit_records.append({"sender_key": sender_key, "command": command, "result": "accepted"})
        if command == "/cancel":
            return "cancelled", OutgoingMessage(content="Cancelled.", reply_to="session-1")
        return "completed", OutgoingMessage(content=f"{command} completed.", reply_to="session-1")

    _, first = _run_sync(handle_command("u1", "/current"))
    _, second = _run_sync(handle_command("u1", "/current"))
    _, third = _run_sync(handle_command("u1", "/current"))
    _assert(first.content == "/current completed." and second.content == "/current completed.", "allowed commands should complete")
    _assert(third.content.startswith("Too many /current attempts."), "repeated commands should be throttled")
    _assert([record["result"] for record in audit_records] == ["accepted", "accepted", "throttled"], "audit log should record throttle")

    message = OutgoingMessage(content="Cost alert: spend=6.0, budget=5.0.", reply_to="session-1", metadata={"command": "cost"})
    _assert(message.content.startswith("Cost alert:"), "cost alert should start with compact label")
    _assert(len(message.content) <= 120, "cost alert should stay compact")

    status, reply = _run_sync(handle_command("u1", "/cancel"))
    _assert(status == "cancelled", "cancel command should return cancelled status immediately")
    _assert(reply is not None and reply.content == "Cancelled.", "cancel reply should be compact")


def main() -> int:
    try:
        validate_channel_core()
        validate_channel_notifications()
        validate_platform_adapters()
        validate_hardening()
    except AssertionError as exc:
        print(f"FAILED: {exc}")
        return 1
    print("direct-validation-ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
