"""Direct verification for LoopDesk gateway loop workspace blockers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.loop_workspace.adapters import McpClient, translate_inbound
from loopdesk.loop_workspace.engine.runner import LoopEngineRunner
from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase
from loopdesk.loop_workspace.service import LoopWorkspaceService


class _RpcContext:
    def __init__(self) -> None:
        self.principal = type(
            "P",
            (),
            {
                "role": "operator",
                "scopes": frozenset(["operator.admin"]),
                "is_owner": True,
                "authenticated": True,
            },
        )()
        self.config = None


def run_git(args: list[str], cwd: Path) -> None:
    completed = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    if completed.stdout.strip():
        print(completed.stdout.strip(), file=sys.stderr)
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)


def main() -> int:
    results = {}
    with Path("/tmp/loopdesk-gateway-verification").mkdir(parents=True, exist_ok=True) or Path("/tmp/loopdesk-gateway-verification") as tmp:
        root = tmp / "workspace"
        root.mkdir(exist_ok=True)
        run_git(["init", "-b", "main"], cwd=root)
        run_git(["config", "user.email", "dev@example.com"], cwd=root)
        run_git(["config", "user.name", "Dev"], cwd=root)
        (root / "README.md").write_text("hello", encoding="utf-8")
        run_git(["add", "README.md"], cwd=root)
        run_git(["commit", "-m", "seed"], cwd=root)

        service = LoopWorkspaceService.from_root(root)
        dispatcher = get_dispatcher()
        ctx = _RpcContext()

        results["registered_loop_workspace_methods"] = sorted(
            name for name in dispatcher.methods() if name.startswith("loop_workspace.")
        )
        results["static_view_files"] = {
            name: getattr(__import__("loopdesk.gateway.control_ui", fromlist=["LOOP_WORKSPACE_VIEW_FILES"]), name)
            for name in ["LOOP_WORKSPACE_VIEW_FILES"]
        }

        start = dispatcher.handle(
            "loop_workspace.engine.start",
            {"root": str(root), "goal": "Ship bounded fix.", "stop_condition": "done"},
            ctx,
        )
        status = dispatcher.handle("loop_workspace.engine.status", {"root": str(root)}, ctx)
        persisted_state = service.repository.read().loop_engine
        results["engine.start.status"] = start["phase"]
        results["engine.status.phase"] = status["phase"]
        results["engine.persisted_iteration"] = persisted_state.get("current_iteration")
        results["engine.start_run_log_present"] = any(
            entry.get("summary") == "Loop engine started." for entry in service.repository.read().run_log
        )

        stop = dispatcher.handle("loop_workspace.engine.stop", {"root": str(root)}, ctx)
        results["engine.stop.phase"] = stop["phase"]
        results["engine.stop_run_log_present"] = any(
            entry.get("summary") == "Loop engine stopped." for entry in service.repository.read().run_log
        )

        detail = dispatcher.handle(
            "loop_workspace.run_log.detail",
            {"root": str(root), "index": -1},
            ctx,
        )
        results["run_log.detail.has_entry"] = isinstance(detail.get("entry"), dict)

        replay = dispatcher.handle("loop_workspace.replay.pack", {"root": str(root)}, ctx)
        results["replay.pack.has_recent_run_log"] = "recent_run_log" in replay
        results["replay.pack.has_templates"] = "templates" in replay

        compact = dispatcher.handle(
            "loop_workspace.session.compact",
            {"root": str(root), "keep_recent": 2},
            ctx,
        )
        results["session.compact.kept"] = compact.get("kept")

        adapter_connect = dispatcher.handle(
            "loop_workspace.adapter.connect",
            {"root": str(root), "command": "python", "args": ["-m", "tests.test_gateway.fake_mcp_server"]},
            ctx,
        )
        adapter_tools = dispatcher.handle("loop_workspace.adapter.list_tools", {"root": str(root)}, ctx)
        tool_result = dispatcher.handle(
            "loop_workspace.adapter.call_tool",
            {"root": str(root), "name": "echo", "arguments": {"text": "hello"}, "workId": "work-1"},
            ctx,
        )
        results["adapter.connected"] = adapter_connect.get("connected") is True
        results["adapter.tools"] = [tool.get("name") for tool in adapter_tools.get("tools", [])]
        results["adapter.tool_result.ok"] = tool_result.get("ok") is True

        service.record_work_item("work-1", "loop", "Draft plan.")
        translated = translate_inbound(
            service,
            {"tool": "fake-mcp", "name": "echo", "workId": "work-1", "toolEvent": tool_result},
        )
        results["translation.run_log_added"] = len(translated["run_log"]) >= 1
        results["post_translation_cost_status"] = service.repository.read().cost_observatory.get("status")

        service.record_approval(
            {"id": "approval-1", "status": "pending", "payload": {"action": "edit"}}
        )
        respond = dispatcher.handle(
            "loop_workspace.approval.respond",
            {"root": str(root), "id": "approval-1", "status": "denied", "payload": {"note": "nope"}},
            ctx,
        )
        results["approval.respond.returns_state"] = isinstance(respond, dict)
        results["approval.respond.denied"] = respond.get("approvals", [{}])[0].get("status") == "denied"
        results["approval.respond.current_work_id_cleared"] = respond.get("current_work_id") is None

        service.record_run_log(
            {
                "source": "loop",
                "workId": "work-history-1",
                "status": "active",
                "summary": "Did work.",
                "cost": {"cost_usd": 0.05, "model": "mock-model"},
            }
        )
        history = dispatcher.handle(
            "loop_workspace.cost.history", {"root": str(root), "limit": 10}, ctx
        )
        results["cost.history.total"] = history.get("total")
        results["cost.history.first_model"] = (history.get("history") or [{}])[0].get("model")

    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
