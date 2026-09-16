"""Test helper to invoke the LoopDesk CLI without importing legacy env."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _REPO_ROOT / "src"
_INVOKER = _REPO_ROOT / "tests" / "support" / "_loop_workspace_invoker.py"


def _cli_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(_SRC_ROOT))
    env["LOOPDESK_GATEWAY_CONFIG_PATH"] = str(cwd / "missing.toml")
    return env


def _extract_json_payload(stdout: str) -> dict[str, object]:
    for candidate in reversed(stdout.splitlines()):
        candidate = candidate.strip()
        if candidate.startswith("{") or candidate.startswith("["):
            return json.loads(candidate)
    raise AssertionError(f"No JSON payload found in CLI output:\n{stdout}")


def invoke_loop(args: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(_INVOKER), *args],
        cwd=cwd,
        env=_cli_env(cwd),
        text=True,
        capture_output=True,
        check=True,
    )
    return _extract_json_payload(completed.stdout)
