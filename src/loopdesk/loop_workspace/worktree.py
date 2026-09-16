"""Git worktree isolation helpers for bounded Goal execution."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout


def _ensure_git_repo(root: Path) -> None:
    if (root / ".git").exists() or any((path / ".git").exists() for path in [root, *root.parents]):
        return
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Dev"], cwd=root, check=True, capture_output=True)
    seed = root / "README.md"
    seed.write_text("loopdesk", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=root, check=True, capture_output=True)


def create_loop_worktree(layout: LoopWorkspaceLayout, worktree_name: str, *, branch: Optional[str] = None) -> Path:
    target = layout.worktrees_dir / worktree_name
    branch_name = branch or f"loopdesk/goal/{worktree_name}"
    _ensure_git_repo(layout.root)
    if target.exists():
        subprocess.run(["git", "worktree", "remove", str(target)], cwd=layout.root, check=False, capture_output=True)
        subprocess.run(["git", "worktree", "prune"], cwd=layout.root, check=False, capture_output=True)
    branch_exists = bool(subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"], cwd=layout.root, check=False, capture_output=True).returncode == 0)
    worktree_args = ["git", "worktree", "add"]
    if branch_exists:
        worktree_args.extend(["-B", branch_name, "--force", str(target), branch_name])
    else:
        worktree_args.extend(["-b", branch_name, "--force", str(target), "main"])
    subprocess.run(worktree_args, cwd=layout.root, check=True, capture_output=True)
    return target


def remove_loop_worktree(layout: LoopWorkspaceLayout, worktree_name: str, *, branch: str | None = None) -> None:
    target = layout.worktrees_dir / worktree_name
    branch_name = branch or f"loopdesk/goal/{worktree_name}"
    subprocess.run(["git", "worktree", "remove", str(target)], cwd=layout.root, check=False, capture_output=True)
    subprocess.run(["git", "worktree", "prune"], cwd=layout.root, check=False, capture_output=True)
    subprocess.run(["git", "branch", "-d", branch_name], cwd=layout.root, check=False, capture_output=True)
    if target.exists():
        target.rmdir()
