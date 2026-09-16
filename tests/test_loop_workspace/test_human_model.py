"""Local human model tests for LoopDesk loop workspaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_human_profile_defaults_to_empty_local_first_payload(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    payload = service.current_state()

    assert payload["human_profile"]["preferences"] == {}
    assert payload["human_profile"]["coding_style"] == {}
    assert payload["human_profile"]["architecture_preference"] == {}
    assert payload["human_profile"]["decision_pattern"] == {}
    assert payload["human_profile"]["review_standard"] == {}
    assert payload["human_profile"]["_meta"]["local_first"] is True
    assert payload["human_profile"]["_meta"]["cloud_sync"] is False
    assert payload["human_profile"]["_meta"]["team_context"] is False


def test_human_profile_can_record_preferences_and_review_standard(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    updated = service.update_human_profile(
        {
            "preferences": {"language": "python"},
            "review_standard": {"require_tests": True},
        }
    )

    payload = updated["human_profile"]
    assert payload["preferences"]["language"] == "python"
    assert payload["review_standard"]["require_tests"] is True
    assert payload["_meta"]["local_first"] is True
