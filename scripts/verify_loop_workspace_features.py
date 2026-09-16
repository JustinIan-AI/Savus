"""Independent feature verification for LoopDesk loop workspace."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

fake_env = ModuleType("loopdesk.env")
fake_env.load_env = lambda *a, **k: 0
fake_env.warn_if_proxy_ignored = lambda *a, **k: None
fake_env.trust_env = lambda *a, **k: False
sys.modules.setdefault("loopdesk.env", fake_env)

from typer.testing import CliRunner
from loopdesk.cli.loop_workspace_cmd import workspace_app
from loopdesk.loop_workspace.adapters import CrossToolAdapter, ToolEvent
from loopdesk.loop_workspace.cli_bridge import LocalCliBridge
from loopdesk.loop_workspace.memory import DurableMemoryIndex
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.templates import load_personal_template
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.worktree import create_loop_worktree, remove_loop_worktree
from loopdesk.gateway.rpc import get_dispatcher


class FakePrincipal:
    role = "operator"
    scopes = frozenset(["operator.admin"])
    is_owner = True
    authenticated = True


class RpcContext:
    def __init__(self) -> None:
        self.principal = FakePrincipal()
        self.config = None


def run_git(args: list[str], cwd: Path) -> None:
    completed = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    if completed.stdout.strip():
        print(completed.stdout.strip(), file=sys.stderr)
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)


def main() -> int:
    results = {}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        repo = tmp / "repo"
        repo.mkdir()
        run_git(["init", "-b", "main"], cwd=repo)
        run_git(["config", "user.email", "dev@example.com"], cwd=repo)
        run_git(["config", "user.name", "Dev"], cwd=repo)
        (repo / "README.md").write_text("hello", encoding="utf-8")
        run_git(["add", "README.md"], cwd=repo)
        run_git(["commit", "-m", "seed"], cwd=repo)
        ws = repo / "workspace"
        service = LoopWorkspaceService.from_root(ws)

        adapter = CrossToolAdapter(service.repository)
        run_log = adapter.translate_event_to_run_log(ToolEvent("codex", "run_goal", {"workId": "goal-1"}))
        state = service.repository.read()
        results["adapter.source"] = run_log["source"]
        results["adapter.summary"] = run_log["summary"]
        results["adapter.current_work_id"] = state.current_work_id
        results["adapter.current_work_source"] = state.current_work_source
        results["adapter.run_log_tail"] = state.run_log[-1]["summary"]

        bridge = LocalCliBridge(service.repository, artifact_dir=service.layout.artifacts_dir)
        bridge_result = bridge.run("codex", ["echo", "delivery"])
        state = service.repository.read()
        results["bridge.ok"] = bridge_result["ok"]
        results["bridge.artifact"] = str(Path(bridge_result["artifact_path"]))
        results["bridge.run_log_has_summary"] = any(entry["summary"] == "codex.run_command completed." for entry in state.run_log)

        memory = DurableMemoryIndex(ws)
        memory.append("Keep retry policy under five attempts", "Avoid unbounded loops.", tags=["reliability"])
        results["memory.search.hits"] = len(memory.search("retry policy"))
        compact = memory.compact(keep_recent=1)
        results["compact.kept"] = compact["kept"]
        results["compact.removed_keys"] = compact["removed_keys"]
        results["compact.files_removed"] = not list((ws / "memory").glob("memory-*.md"))

        runner = CliRunner()
        init = runner.invoke(workspace_app, ["init", str(ws), "--json"], catch_exceptions=False)
        results["cli.init.exit_code"] = init.exit_code
        results["cli.init.output"] = init.output.strip()
        results["cli.init.status"] = json.loads(init.output.strip())["status"]

        show = runner.invoke(workspace_app, ["show", str(ws), "--json"], catch_exceptions=False)
        results["cli.show.status"] = json.loads(show.output.strip())["status"]

        template = load_personal_template("backend-engineer")
        service.ensure_initialized(intent="Ship bounded API fix.", selected_template=template.id)
        state = service.record_work_item("work-2", "loop", f"Use {template.name} for discovery.")
        results["template.selected_template"] = state["selected_template"]
        results["template.project_name"] = state["project_name"]

        dispatcher = get_dispatcher()
        root = str(ws)
        create = dispatcher.handle("loop_workspace.create", {"root": root}, RpcContext())
        update = dispatcher.handle("loop_workspace.update", {"root": root, "intent": "Ship bounded fix.", "status": "active"}, RpcContext())
        resume = dispatcher.handle("loop_workspace.resume", {"root": root, "workId": "work-1", "summary": "Resume work.", "source": "ui"}, RpcContext())
        getp = dispatcher.handle("loop_workspace.get", {"root": root}, RpcContext())
        run_log_payload = dispatcher.handle("loop_workspace.record_run_log", {"root": root, "source": "loop", "workId": "work-1", "status": "completed", "summary": "Completed bounded task.", "cost": {"cost_usd": 0.12}}, RpcContext())
        kill = dispatcher.handle("loop_workspace.set_kill_switch", {"root": root, "enabled": True}, RpcContext())
        context = dispatcher.handle("loop_workspace.context_pack", {"root": root}, RpcContext())
        worktree_payload = dispatcher.handle("loop_workspace.worktree.create", {"root": root, "workId": "goal-1"}, RpcContext())
        listing = dispatcher.handle("loop_workspace.list", {"root": str(ws.parent)}, RpcContext())
        export = dispatcher.handle("loop_workspace.export", {"root": root, "output": str(ws / "exported.json")}, RpcContext())
        results["rpc.create.status"] = create.get("status") or create.get("ok", {}).get("status")
        results["rpc.update.intent"] = update["intent"]
        results["rpc.resume.work_id"] = resume["current_work_id"]
        results["rpc.resume.source"] = resume["current_work_source"]
        results["rpc.get.work_id"] = getp["current_work_id"]
        results["rpc.run_log.spend"] = run_log_payload["cost_observatory"]["spend_usd"]
        results["rpc.kill.enabled"] = kill["safety"]["kill_switch_enabled"]
        results["rpc.context.work_id"] = context["current_work_id"]
        results["rpc.worktree.exists"] = Path(worktree_payload["path"]).exists()
        results["rpc.list.count"] = len(listing["workspaces"])
        results["rpc.export.exists"] = Path(export["path"]).exists()

        memory.compact(keep_recent=1)
        results["memory.compact.order_stable"] = all(
            path.exists() is False
            for path in (ws / "memory").glob("memory-*.md")
        )

        target = create_loop_worktree(LoopWorkspaceLayout.ensure(repo), "goal-alpha")
        listed = service.list_worktrees()
        results["worktree.created"] = target.exists()
        results["worktree.listed_name"] = listed["worktrees"][0]["name"]
        remove_loop_worktree(LoopWorkspaceLayout.ensure(repo), "goal-alpha")
        results["worktree.removed"] = not target.exists()
        results["worktree.listed_empty"] = service.list_worktrees()["worktrees"] == []

    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
