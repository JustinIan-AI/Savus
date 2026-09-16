"""Subprocess helper so loop workspace CLI tests never import legacy env."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_CWD = Path.cwd()
_REPO_ROOT = Path(__file__).resolve()
for candidate in (_REPO_ROOT.parents[1], _REPO_ROOT.parents[0], _CWD):
    if (candidate / "pyproject.toml").exists() or (candidate / "src" / "loopdesk").exists():
        _REPO_ROOT = candidate
        break
_SRC_ROOT = _REPO_ROOT / "src"


class _FakeEnvModule:
    load_env = lambda *args, **kwargs: 0
    warn_if_proxy_ignored = lambda *args, **kwargs: None
    trust_env = lambda *args, **kwargs: False


if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))
sys.modules.setdefault("loopdesk.env", _FakeEnvModule())

from typer.testing import CliRunner  # noqa: E402
from loopdesk.cli.main import app  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:] or ["--help"]
    result = CliRunner().invoke(app, args, catch_exceptions=False, standalone_mode=False)
    output = result.output
    payload = None
    for candidate in output.splitlines():
        candidate = candidate.strip()
        if candidate.startswith("{") or candidate.startswith("["):
            payload = candidate
            break
    if payload is None:
        raise SystemExit(f"No JSON payload found in CLI output:\n{output}")
    sys.stdout.write(payload + "\n")
