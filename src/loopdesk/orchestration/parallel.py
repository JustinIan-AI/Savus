from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

@dataclass
class FanOutResult:
    winner_agent: str
    winner_worktree: str
    winning_score: float

class WorktreeFanOutExecutor:
    """Executes candidate agent solutions in isolated git worktrees and selects the winner."""
    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root).resolve()
        self.active_worktrees: list[Path] = []

    def create_worktree(self, branch_name: str, worktree_dir: Path | str) -> Path:
        wt_path = Path(worktree_dir).resolve()
        wt_path.parent.mkdir(parents=True, exist_ok=True)
        # git worktree add -b <branch> <path>
        cmd = ["git", "worktree", "add", "-b", branch_name, str(wt_path)]
        res = subprocess.run(cmd, cwd=str(self.repo_root), capture_output=True, text=True)
        if res.returncode != 0:
            # Try without -b if branch already exists
            cmd_fallback = ["git", "worktree", "add", str(wt_path), branch_name]
            res_fallback = subprocess.run(cmd_fallback, cwd=str(self.repo_root), capture_output=True, text=True)
            if res_fallback.returncode != 0:
                raise RuntimeError(f"Failed to create worktree: {res.stderr or res_fallback.stderr}")
        self.active_worktrees.append(wt_path)
        return wt_path

    def remove_worktree(self, worktree_dir: Path | str, force: bool = True) -> None:
        wt_path = Path(worktree_dir).resolve()
        cmd = ["git", "worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(str(wt_path))
        subprocess.run(cmd, cwd=str(self.repo_root), capture_output=True, text=True)
        if wt_path in self.active_worktrees:
            self.active_worktrees.remove(wt_path)
        if wt_path.exists():
            shutil.rmtree(wt_path, ignore_errors=True)

    def cleanup_all(self) -> None:
        for wt in list(self.active_worktrees):
            self.remove_worktree(wt)

    def select_winner(self, candidates: List[Dict[str, Any]]) -> FanOutResult:
        if not candidates:
            raise ValueError("No candidates provided for winner selection")

        best = max(candidates, key=lambda c: (c.get("score", 0), c.get("passed_tests", 0)))
        return FanOutResult(
            winner_agent=best["agent"],
            winner_worktree=best["worktree"],
            winning_score=best.get("score", 0.0)
        )
