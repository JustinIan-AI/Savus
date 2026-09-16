"""Static guardrail tests for LoopDesk v1.1 docs."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
V11_DOC_PATTERNS = [
    "docs/guides/guided-handoff.md",
    "docs/releases/loopdesk-v1.1.md",
    "docs/acceptance/loopdesk-v1.1-acceptance-checklist.md",
    "docs/decisions/handoff-cli-surface.md",
    "docs/prd/personal-loop-workspace-v1.1.zh.md",
    "README.product.md",
]


def _doc_paths() -> list[Path]:
    paths = []
    for pattern in V11_DOC_PATTERNS:
        paths.extend(REPO_ROOT.glob(pattern))
    return sorted({path for path in paths if path.is_file()})


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_guided_handoff_doc_exists_and_mentions_project_loop_worktree_resume() -> None:
    paths = [path for path in _doc_paths() if path.name == "guided-handoff.md"]
    assert paths, "missing guided handoff doc"
    text = _load_text(paths[0])
    lowered = text.lower()
    for token in ["project", "loop", "worktree", "resume"]:
        assert token in lowered, f"missing handoff token: {token}"


def test_anti_room_guardrail_docs_do_not_leak_team_room_or_cloud_sync() -> None:
    banned_phrases = ["team room", "team-room", "cloud sync", "cloud-sync", "IM-first", "IM first"]
    rejection_markers = ["loopdesk 不做", "loopdesk does not", "must not", "must not imply", "不得"]
    offenders = []
    for path in _doc_paths():
        lowered = _load_text(path).lower()
        hits = []
        for phrase in banned_phrases:
            if phrase.lower() not in lowered:
                continue
            if any(marker in lowered for marker in rejection_markers):
                continue
            hits.append(phrase)
        if hits:
            offenders.append(f"{path}: {hits}")
    assert not offenders, "guardrail leaks found: " + " | ".join(offenders)


def test_human_profile_is_described_as_local_first_and_inspectable() -> None:
    text = _load_text(REPO_ROOT / "docs/prd/personal-loop-workspace-v1.1.zh.md")
    lowered = text.lower()
    assert "human profile" in lowered or "human_profile" in lowered
    assert "local-first" in lowered
    assert "inspectable" in lowered
