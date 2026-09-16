from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.worktree import create_loop_worktree, remove_loop_worktree


def test_create_loop_worktree_creates_branch_and_path(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    layout = LoopWorkspaceLayout.ensure(tmp_path / "workspace")

    target = create_loop_worktree(layout, "goal-alpha")

    assert target.exists()
    assert (layout.worktrees_dir / "goal-alpha").exists()


def test_remove_loop_worktree_cleans_branch_and_path(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    layout = LoopWorkspaceLayout.ensure(tmp_path / "workspace")
    create_loop_worktree(layout, "goal-beta")

    remove_loop_worktree(layout, "goal-beta")

    assert not (layout.worktrees_dir / "goal-beta").exists()


def _init_git_repo(path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Dev"], cwd=path, check=True, capture_output=True)
    (path / "README.md").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=path, check=True, capture_output=True)
