"""Release and acceptance evidence tests for LoopDesk v1.1."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v11_release_notes_exist_and_mention_runtime_matrix_and_desktop_boundary() -> None:
    release_notes = REPO_ROOT / "docs/releases/loopdesk-v1.1.md"
    assert release_notes.is_file(), "missing v1.1 release notes"
    text = release_notes.read_text(encoding="utf-8")
    assert "runtime matrix" in text.lower()
    assert "desktop" in text.lower()


def test_v11_acceptance_checklist_references_focused_test_commands() -> None:
    checklist = REPO_ROOT / "docs/acceptance/loopdesk-v1.1-acceptance-checklist.md"
    assert checklist.is_file(), "missing v1.1 acceptance checklist"
    text = checklist.read_text(encoding="utf-8")
    assert "pytest" in text
    assert "handoff" in text.lower()
    assert "human" in text.lower()
