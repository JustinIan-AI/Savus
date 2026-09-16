"""Git-backed fixtures for loop workspace worktree scenarios."""

from __future__ import annotations

import subprocess
from pathlib import Path


def init_git_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if not (path / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Dev"], cwd=path, check=True, capture_output=True)
        (path / "README.md").write_text("hello", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "seed"], cwd=path, check=True, capture_output=True)
