from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TIER_A_MYPY_PARTITION: tuple[str, ...] = (
    "src/loopdesk/tool_boundary.py",
    "src/loopdesk/tools/boundary.py",
    "src/loopdesk/gateway/session_services.py",
    "src/loopdesk/memory/protocols.py",
    "src/loopdesk/provider/protocol.py",
    "src/loopdesk/provider/openai.py",
    "src/loopdesk/session/compaction.py",
    "src/loopdesk/scheduler/routing.py",
    "src/loopdesk/scheduler/delivery.py",
    "src/loopdesk/scheduler/handlers.py",
    "src/loopdesk/skills/hub/installer.py",
    "src/loopdesk/skills/hub/scanner.py",
    "src/loopdesk/skills/hub/lockfile.py",
    "src/loopdesk/mcp/discovery.py",
    "src/loopdesk/tools/builtin/web.py",
)


def test_tier_a_mypy_partition_stays_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mypy", *TIER_A_MYPY_PARTITION],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout
