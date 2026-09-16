"""Focused gateway tests for LoopDesk v0.2 channel notification formatting."""

from __future__ import annotations

import pytest

from loopdesk.channels.types import ChannelNotificationFormatter, OutgoingMessage


def test_status_notification_uses_compact_workspace_summary() -> None:
    formatter = ChannelNotificationFormatter()
    message = formatter.format_status({"status": "active", "current_work_summary": "Refactor channel adapters"})

    assert message == "LoopDesk status: active; Refactor channel adapters"


def test_approval_notification_includes_compact_reply_hint() -> None:
    formatter = ChannelNotificationFormatter()
    message = formatter.format_approval_request({"approval_id": "approval-1", "summary": "Run bounded goal"})

    assert message.startswith("Approval needed (approval-1): Run bounded goal.")
    assert "/approve" in message
    assert "/reject" in message


def test_cost_alert_does_not_expose_raw_run_log_payload() -> None:
    formatter = ChannelNotificationFormatter()
    message = formatter.format_cost_alert({"spend_usd": 4.2, "budget_cap_usd": 5.0, "run_log": [{"secret": "x"}]})

    assert "secret" not in message
    assert message.startswith("Cost alert:")


def test_run_summary_truncates_long_loop_results() -> None:
    formatter = ChannelNotificationFormatter()
    long_summary = "Loop finished: " + "x" * 140
    message = formatter.format_run_summary({"status": "completed", "summary": long_summary})

    assert message.startswith("Loop result: completed. Loop finished:")
    assert len(message) <= 120
    assert message.endswith("...")


def test_outgoing_message_limits_metadata_payload_for_plain_text_fallback() -> None:
    message = OutgoingMessage(
        content="ok",
        reply_to="thread-1",
        metadata={"command": "compact", "large_payload": "x" * 500},
    )

    assert len(message.content) <= 500
    assert message.reply_to == "thread-1"
    assert message.metadata["command"] == "compact"
