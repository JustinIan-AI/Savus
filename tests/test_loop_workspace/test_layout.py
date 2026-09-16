"""Layout tests for LoopDesk loop workspaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_default_layout_creates_required_paths(tmp_path: Path) -> None:
    workspace = tmp_path / "loop"
    workspace.mkdir()

    service = LoopWorkspaceService.from_root(workspace)
    layout = service.layout

    assert layout.root == workspace
    assert layout.state_file.exists()
    assert layout.memory_dir.exists()
    assert layout.skills_dir.exists()
    assert layout.artifacts_dir.exists()
    assert layout.worktrees_dir.exists()
    assert layout.personal_templates_dir.exists()
    assert layout.memory_index_path.exists()


def test_layout_rejects_paths_outside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "loop"
    workspace.mkdir()
    layout = LoopWorkspaceLayout.ensure(workspace)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError):
        layout.require_under_workspace(outside / "secret.txt")
