"""Focused verification script for legacy MCP stdio and gateway subsets."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRECT_SUBSET = [
    "tests/test_loop_workspace/test_mcp_stdio.py",
    "tests/test_loop_workspace/test_mcp_stdio_process.py",
    "tests/test_loop_workspace/test_mcp_stdio_debug.py",
]
GATEWAY_SUBSET = [
    "tests/test_gateway/test_rpc_loop_workspace.py",
    "tests/test_gateway/test_rpc_loop_workspace_extended.py",
    "tests/test_gateway/test_loop_workspace_view_static.py",
    "tests/test_gateway/test_loop_workspace_panels.py",
    "tests/test_gateway/test_no_head_blocking.py",
    "tests/test_gateway/test_no_split_brain_lock.py",
    "tests/test_gateway/test_graceful_shutdown_drain.py",
    "tests/test_gateway/test_force_reset_drain.py",
    "tests/test_gateway/test_pidfile_lock.py",
]
DEFAULT_TIMEOUT = 180


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify MCP stdio and gateway stability subsets.")
    parser.add_argument("--subset", choices=["all", "direct", "gateway"], default="all")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-subset timeout in seconds.")
    return parser.parse_args()


def _ensure_workspace() -> None:
    workspace = Path("/tmp/loopdesk-mcp-smoke")
    workspace.mkdir(parents=True, exist_ok=True)
    if (workspace / "LOOP-STATE.json").exists():
        return
    command = [
        sys.executable,
        "-I",
        "-c",
        """
from pathlib import Path
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService

root = LoopWorkspaceLayout.ensure(Path('/tmp/loopdesk-mcp-smoke'))
service = LoopWorkspaceService.from_root(root)
service.ensure_initialized(intent='MCP integration', selected_template='backend-engineer')
service.record_work_item('work-1', 'loop', 'Validate MCP handoff.')
service.set_kill_switch(True)
service.set_denylist(['dangerous.sh'])
print(root)
""",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        print("[direct] workspace bootstrap failed")
        print((completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else ""))
        raise SystemExit(1)


def _run_direct_smoke(timeout: int) -> int:
    _ensure_workspace()
    command = [
        sys.executable,
        "-I",
        "-c",
        """
from pathlib import Path
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService
from tests.support.mcp_workspace_client import build_client, call_tool, initialize_client, list_tools

root = LoopWorkspaceLayout.ensure(Path('/tmp/loopdesk-mcp-smoke'))
service = LoopWorkspaceService.from_root(root)
service.ensure_initialized(intent='MCP integration', selected_template='backend-engineer')
service.record_work_item('work-1', 'loop', 'Validate MCP handoff.')
service.set_kill_switch(True)
service.set_denylist(['dangerous.sh'])

client = build_client(root, in_process=True)
initialize_client(client)
tools = [tool['name'] for tool in list_tools(client)]
assert tools == [
    'loopdesk.get_context_pack',
    'loopdesk.list_templates',
    'loopdesk.read_template',
    'loopdesk.run_local_command',
], tools
context_pack = call_tool(client, 'loopdesk.get_context_pack', {})
assert context_pack['current_work_id'] == 'work-1'
assert context_pack['selected_template'] == 'backend-engineer'
assert context_pack['safety']['kill_switch_enabled'] is True
assert context_pack['safety']['denylist'] == ['dangerous.sh']
template = call_tool(client, 'loopdesk.read_template', {'template_id': 'backend-engineer'})
assert template['name'] == 'Backend Implementation'
assert template['loop_steps'][0] == 'Review failing tests, issues, and task backlog.'
command = call_tool(client, 'loopdesk.run_local_command', {'argv': ['printf', 'mcp-handoff\\n'], 'work_id': 'work-1'})
assert command['ok'] is True
assert command['stdout'].strip() == 'mcp-handoff'
""",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        print("[direct] smoke exit code:", completed.returncode)
        if completed.stdout.strip():
            print(completed.stdout.strip())
        if completed.returncode != 0:
            print(completed.stderr.strip() or completed.stdout.strip())
        return completed.returncode
    except subprocess.TimeoutExpired:
        print(f"[direct] timed out after {timeout} seconds")
        return 1


def _run_pytest_subset(suite: str, paths: list[str], timeout: int) -> int:
    if not paths:
        print(f"[{suite}] no tests selected")
        return 0
    command = [
        sys.executable,
        "-I",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "-o",
        "addopts=",
        *paths,
    ]
    print(f"[{suite}] running:", " ".join(paths))
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        print(f"[{suite}] exit code:", completed.returncode)
        output = (completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else "")
        print(output.strip() or "(no output)")
        return completed.returncode
    except subprocess.TimeoutExpired:
        print(f"[{suite}] timed out after {timeout} seconds")
        return 1


def main() -> int:
    args = _parse_args()
    failures = []
    if args.subset in {"all", "direct"}:
        if _run_direct_smoke(args.timeout) != 0:
            failures.append("direct")
    if args.subset in {"all", "gateway"}:
        if _run_pytest_subset("gateway", GATEWAY_SUBSET, args.timeout) != 0:
            failures.append("gateway")
    if args.subset in {"all", "direct"}:
        if _run_pytest_subset("direct", DIRECT_SUBSET, args.timeout) != 0:
            failures.append("direct-pytest")
    if failures:
        print("failed subsets:", ", ".join(failures))
        return 1
    print("all requested subsets passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
