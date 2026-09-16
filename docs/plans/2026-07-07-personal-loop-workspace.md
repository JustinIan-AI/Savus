# Personal Loop Workspace v0.1 Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a local-first personal loop workspace that lets an independent developer carry context, memory, loop state, and safety controls across Claude Code, Codex, Codebuddy, Trae, Gemini, and local CLIs.

**Architecture:** Extend the existing OpenSquilla runtime with a new loop workspace layer that owns portable state, loop scheduling, cross-tool adapters, and developer-facing CLI/RPC surfaces while reusing gateway, session, memory, skill, cost, and approval infrastructure.

**Tech Stack:** Python 3.12, Starlette, Typer, SQLite/SQLModel, APScheduler, croniter, Git worktrees, MCP/ACP adapter surfaces.

---

### Task 1: Add loop workspace state schema and serialization

**Files:**
- Create: `src/loopdesk/loop_workspace/schema.py`
- Create: `src/loopdesk/loop_workspace/serialization.py`
- Test: `tests/test_loop_workspace/test_schema.py`

**Step 1: Write the failing test**

```python
def test_default_loop_state_round_trip(tmp_path: Path) -> None:
    state = LoopWorkspaceState.create(
        workspace_root=tmp_path,
        intent="Implement loop handoff between Codex and Claude Code.",
        tags=["codex", "claude-code", "handoff"],
    )

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.schema_version == 1
    assert restored.workspace_root == tmp_path
    assert restored.status == LoopWorkspaceStatus.PLANNED
    assert restored.intent == state.intent
    assert restored.tags == state.tags
    assert restored.updated_at >= restored.created_at
```

Run: `pytest tests/test_loop_workspace/test_schema.py::test_default_loop_state_round_trip -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'loopdesk.loop_workspace'`

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class LoopWorkspaceStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LoopWorkspaceState:
    def __init__(
        self,
        *,
        workspace_root: Path,
        intent: str,
        status: LoopWorkspaceStatus = LoopWorkspaceStatus.PLANNED,
        schema_version: int = 1,
        loop_id: str | None = None,
        active_tool: str | None = None,
        last_tool: str | None = None,
        last_result: str | None = None,
        tags: list[str] | None = None,
        preferences: dict[str, Any] | None = None,
        decisions: list[dict[str, Any]] | None = None,
        artifacts: list[dict[str, Any]] | None = None,
        lessons: list[dict[str, Any]] | None = None,
        override_history: list[dict[str, Any]] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.schema_version = int(schema_version)
        self.loop_id = loop_id
        self.workspace_root = Path(workspace_root).resolve()
        self.intent = intent.strip()
        self.status = status
        self.active_tool = active_tool
        self.last_tool = last_tool
        self.last_result = last_result
        self.tags = list(tags or [])
        self.preferences = dict(preferences or {})
        self.decisions = list(decisions or [])
        self.artifacts = list(artifacts or [])
        self.lessons = list(lessons or [])
        self.override_history = list(override_history or [])
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(cls, workspace_root: Path, intent: str, tags: list[str] | None = None) -> "LoopWorkspaceState":
        return cls(
            workspace_root=workspace_root,
            intent=intent,
            tags=tags or [],
        )

    def record_override(self, source: str, reason: str, previous_status: LoopWorkspaceStatus) -> None:
        self.override_history.append(
            {
                "source": source,
                "reason": reason,
                "previous_status": previous_status.value,
                "next_status": self.status.value,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "loop_id": self.loop_id,
            "workspace_root": str(self.workspace_root),
            "intent": self.intent,
            "status": self.status.value,
            "active_tool": self.active_tool,
            "last_tool": self.last_tool,
            "last_result": self.last_result,
            "tags": self.tags,
            "preferences": self.preferences,
            "decisions": self.decisions,
            "artifacts": self.artifacts,
            "lessons": self.lessons,
            "override_history": self.override_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LoopWorkspaceState":
        return cls(
            schema_version=int(payload.get("schema_version", 1)),
            loop_id=payload.get("loop_id"),
            workspace_root=Path(payload.get("workspace_root", ".")),
            intent=str(payload.get("intent", "")),
            status=LoopWorkspaceStatus(str(payload.get("status", LoopWorkspaceStatus.PLANNED.value))),
            active_tool=payload.get("active_tool"),
            last_tool=payload.get("last_tool"),
            last_result=payload.get("last_result"),
            tags=list(payload.get("tags") or []),
            preferences=dict(payload.get("preferences") or {}),
            decisions=list(payload.get("decisions") or []),
            artifacts=list(payload.get("artifacts") or []),
            lessons=list(payload.get("lessons") or []),
            override_history=list(payload.get("override_history") or []),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            updated_at=datetime.fromisoformat(str(payload["updated_at"])),
        )
```

Run: `pytest tests/test_loop_workspace/test_schema.py::test_default_loop_state_round_trip -v`
Expected: PASS

**Step 3: Add schema/state tests**

```python
def test_status_change_records_override_history() -> None:
    state = LoopWorkspaceState.create(workspace_root=tmp_path, intent="Review PRD and draft plan.")
    previous = state.status
    state.status = LoopWorkspaceStatus.BLOCKED
    state.record_override(source="loop-engine", reason="Awaiting MCP adapter confirmation.", previous_status=previous)

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.status == LoopWorkspaceStatus.BLOCKED
    assert len(restored.override_history) == 1
    assert restored.override_history[0]["source"] == "loop-engine"
```

Run: `pytest tests/test_loop_workspace/test_schema.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/loop_workspace/schema.py src/loopdesk/loop_workspace/serialization.py tests/test_loop_workspace/test_schema.py
git commit -m "feat(loop_workspace): add portable loop state schema"
```

---

### Task 2: Add loop workspace filesystem layout and helper APIs

**Files:**
- Create: `src/loopdesk/loop_workspace/layout.py`
- Create: `src/loopdesk/loop_workspace/helpers.py`
- Test: `tests/test_loop_workspace/test_layout.py`

**Step 1: Write the failing test**

```python
def test_default_layout_creates_required_paths(tmp_path: Path) -> None:
    workspace = tmp_path / "loop"
    workspace.mkdir()

    layout = LoopWorkspaceLayout.ensure(workspace)

    assert layout.root == workspace
    assert layout.state_file.exists()
    assert layout.memory_dir.exists()
    assert layout.skills_dir.exists()
    assert layout.artifacts_dir.exists()
    assert layout.worktrees_dir.exists()
```

Run: `pytest tests/test_loop_workspace/test_layout.py::test_default_layout_creates_required_paths -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoopWorkspaceLayout:
    root: Path
    state_file: Path
    memory_dir: Path
    skills_dir: Path
    artifacts_dir: Path
    worktrees_dir: Path

    @classmethod
    def ensure(cls, root: Path) -> "LoopWorkspaceLayout":
        root = Path(root).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        state_file = root / "LOOP-STATE.json"
        memory_dir = root / "memory"
        skills_dir = root / "skills"
        artifacts_dir = root / "artifacts"
        worktrees_dir = root / ".loop-worktrees"
        for directory in (memory_dir, skills_dir, artifacts_dir, worktrees_dir):
            directory.mkdir(parents=True, exist_ok=True)
        state_file.touch(exist_ok=True)
        return cls(
            root=root,
            state_file=state_file,
            memory_dir=memory_dir,
            skills_dir=skills_dir,
            artifacts_dir=artifacts_dir,
            worktrees_dir=worktrees_dir,
        )

    def worktree_path(self, loop_id: str) -> Path:
        return self.worktrees_dir / loop_id
```

**Step 3: Add layout tests**

```python
def test_state_file_path_is_relative_to_root() -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)

    assert layout.state_file == layout.root / "LOOP-STATE.json"
    assert layout.state_file.is_relative_to(layout.root)
```

Run: `pytest tests/test_loop_workspace/test_layout.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/loop_workspace/layout.py src/loopdesk/loop_workspace/helpers.py tests/test_loop_workspace/test_layout.py
git commit -m "feat(loop_workspace): add workspace layout and path helpers"
```

---

### Task 3: Add Git worktree isolation helper for loop runs

**Files:**
- Create: `src/loopdesk/loop_workspace/worktrees.py`
- Test: `tests/test_loop_workspace/test_worktrees.py`

**Step 1: Write the failing test**

```python
def test_create_loop_worktree_creates_detached_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# repo", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "dev@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Dev"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "seed"], check=True)

    manager = GitWorktreeManager(repo)
    target = tmp_path / "loop-worktree"

    worktree = manager.create_worktree(loop_id="loop-1", target=target)

    assert worktree.exists()
    assert worktree / "README.md" exists
    manager.remove_worktree(loop_id="loop-1")
    assert not worktree.exists()
```

Run: `pytest tests/test_loop_workspace/test_worktrees.py::test_create_loop_worktree_creates_detached_worktree -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

import subprocess
from pathlib import Path

from loopdesk.loop_workspace.helpers import LoopWorkspaceLayout


class GitWorktreeError(Exception):
    pass


class GitWorktreeManager:
    def __init__(self, repo: Path) -> None:
        self.repo = Path(repo).expanduser().resolve()

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                ["git", "-C", str(self.repo), *args],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise GitWorktreeError("git is not installed or not on PATH") from exc
        except subprocess.CalledProcessError as exc:
            raise GitWorktreeError(exc.stderr.strip() or str(exc)) from exc

    def create_worktree(self, loop_id: str, target: Path) -> Path:
        target = Path(target).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        self._git("worktree", "add", "--detach", str(target))
        return target

    def remove_worktree(self, loop_id: str) -> None:
        layout = LoopWorkspaceLayout(self.repo)
        target = layout.worktree_path(loop_id)
        if target.exists():
            self._git("worktree", "remove", str(target))
```

**Step 3: Add worktree tests**

```python
def test_missing_git_raises_managed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "")

    with pytest.raises(GitWorktreeError, match="git is not installed"):
        GitWorktreeManager(tmp_path).create_worktree("loop-1", tmp_path / "wt")
```

Run: `pytest tests/test_loop_workspace/test_worktrees.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/loop_workspace/worktrees.py tests/test_loop_workspace/test_worktrees.py
git commit -m "feat(loop_workspace): add git worktree isolation helper"
```

---

### Task 4: Add loop workspace state service with persistence and export

**Files:**
- Create: `src/loopdesk/loop_workspace/service.py`
- Create: `src/loopdesk/loop_workspace/repository.py`
- Test: `tests/test_loop_workspace/test_service.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_service_persists_and_exports_loop_state(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)

    state = await service.create_state(
        intent="Draft PRD, then implement v0.1 loop commands.",
        tags=["prd", "v0.1"],
        worktree_path=tmp_path / "wt",
    )
    await service.update_state(
        state.loop_id,
        status=LoopWorkspaceStatus.ACTIVE,
        active_tool="codex",
        last_tool="claude-code",
        decisions=[{"decision": "Use MCP-first adapters", "decided_at": datetime.now(timezone.utc).isoformat()}],
    )

    exported = await service.export_context(state.loop_id)
    restored = await service.import_context(exported)

    assert restored.status == LoopWorkspaceStatus.ACTIVE
    assert restored.active_tool == "codex"
    assert restored.last_tool == "claude-code"
    assert any(decision["decision"] == "Use MCP-first adapters" for decision in restored.decisions)
    assert (layout.artifacts_dir / "context-export.json").exists()
```

Run: `pytest tests/test_loop_workspace/test_service.py::test_service_persists_and_exports_loop_state -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loopdesk.loop_workspace.schema import LoopWorkspaceState, LoopWorkspaceStatus
from loopdesk.loop_workspace.helpers import LoopWorkspaceLayout


class LoopWorkspaceService:
    def __init__(self, layout: LoopWorkspaceLayout) -> None:
        self.layout = layout
        self._states: dict[str, LoopWorkspaceState] = {}

    async def create_state(
        self,
        intent: str,
        tags: list[str] | None = None,
        worktree_path: Path | None = None,
    ) -> LoopWorkspaceState:
        loop_id = f"loop-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        state = LoopWorkspaceState.create(
            workspace_root=self.layout.root,
            intent=intent,
            tags=tags or [],
        )
        state.loop_id = loop_id
        state.preferences["worktree_path"] = str(worktree_path) if worktree_path else ""
        self._states[loop_id] = state
        await self._persist(state)
        return state

    async def get_state(self, loop_id: str) -> LoopWorkspaceState:
        return self._states[loop_id]

    async def update_state(self, loop_id: str, **changes: Any) -> LoopWorkspaceState:
        state = self._states[loop_id]
        previous_status = state.status
        for key, value in changes.items():
            if key == "status":
                value = LoopWorkspaceStatus(str(value))
            setattr(state, key, value)
        if "status" in changes:
            state.record_override(source="service", reason="manual update", previous_status=previous_status)
        state.updated_at = datetime.now(timezone.utc)
        await self._persist(state)
        return state

    async def _persist(self, state: LoopWorkspaceState) -> None:
        self.layout.state_file.write_text(
            json.dumps(state.to_dict(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

    async def export_context(self, loop_id: str) -> Path:
        state = self._states[loop_id]
        destination = self.layout.artifacts_dir / "context-export.json"
        destination.write_text(
            json.dumps(state.to_dict(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return destination

    async def import_context(self, source: Path) -> LoopWorkspaceState:
        payload = json.loads(Path(source).read_text(encoding="utf-8"))
        state = LoopWorkspaceState.from_dict(payload)
        self._states[state.loop_id or payload["loop_id"]] = state
        await self._persist(state)
        return state
```

**Step 3: Add service tests**

```python
def test_create_state_populates_worktree_preference(tmp_path: Path) -> None:
    service = LoopWorkspaceService(LoopWorkspaceLayout.ensure(tmp_path))
    state = asyncio.run(service.create_state("Review docs", worktree_path=tmp_path / "wt"))

    assert state.loop_id is not None
    assert service._states[state.loop_id].preferences["worktree_path"] == str(tmp_path / "wt")
```

Run: `pytest tests/test_loop_workspace/test_service.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/loop_workspace/service.py src/loopdesk/loop_workspace/repository.py tests/test_loop_workspace/test_service.py
git commit -m "feat(loop_workspace): add state service, persistence, and context export"
```

---

### Task 5: Add loop workspace CLI surface with state commands

**Files:**
- Create: `src/loopdesk/cli/loop_workspace_cmd.py`
- Modify: `src/loopdesk/cli/main.py:26-34`
- Test: `tests/test_cli/test_loop_workspace_cmd.py`

**Step 1: Write the failing test**

```python
from loopdesk.cli import loop_workspace_cmd


def test_loop_workspace_init_creates_state_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = loop_workspace_cmd.init_loop_workspace(
        path=tmp_path,
        intent="Review PRD and plan v0.1.",
        json_output=False,
    )

    assert exit_code == 0
    assert (tmp_path / "LOOP-STATE.json").exists()
    assert "Review PRD and plan v0.1." in (tmp_path / "LOOP-STATE.json").read_text(encoding="utf-8")
```

Run: `pytest tests/test_cli/test_loop_workspace_cmd.py::test_loop_workspace_init_creates_state_file -v`
Expected: FAIL with `ModuleNotFoundError` or attribute error

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

import json
from pathlib import Path

import typer

from loopdesk.loop_workspace.helpers import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.schema import LoopWorkspaceState


app = typer.Typer(help="Manage personal loop workspace state.")


@app.command("init")
def init_loop_workspace(
    path: Path = typer.Option(Path("."), help="Loop workspace root"),
    intent: str = typer.Option(..., help="Initial loop intent to persist"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    layout = LoopWorkspaceLayout.ensure(path)
    service = LoopWorkspaceService(layout)
    state = asyncio.run(service.create_state(intent=intent))
    if json_output:
        typer.echo(json.dumps(state.to_dict(), sort_keys=True, indent=2))
        raise typer.Exit(code=0)
    typer.echo(f"Initialized loop workspace at {layout.root}")
    typer.echo(f"State file: {layout.state_file}")


@app.command("show")
def show_loop_workspace(
    path: Path = typer.Option(Path("."), help="Loop workspace root"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    layout = LoopWorkspaceLayout.ensure(path)
    payload = json.loads(layout.state_file.read_text(encoding="utf-8") or "{}")
    if json_output:
        typer.echo(json.dumps(payload, sort_keys=True, indent=2))
        raise typer.Exit(code=0)
    typer.echo(f"Loop workspace: {layout.root}")
    typer.echo(f"Status: {payload.get('status', 'unknown')}")
    typer.echo(f"Intent: {payload.get('intent', '')}")
```

**Step 3: Register the CLI and add tests**

Modify `src/loopdesk/cli/main.py:27` by adding:

```python
from loopdesk.cli.loop_workspace_cmd import app as loop_workspace_app  # noqa: E402
```

Add registration near the existing `app.add_typer(...)` block:

```python
app.add_typer(loop_workspace_app, name="loop")
```

Add CLI tests:

```python
def test_loop_workspace_show_reads_existing_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [sys.executable, "-m", "loopdesk", "loop", "init", "--intent", "Ship v0.1."],
        check=True,
        cwd=tmp_path,
    )
    result = subprocess.run(
        [sys.executable, "-m", "loopdesk", "loop", "show", "--json"],
        check=True,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["intent"] == "Ship v0.1."
    assert payload["status"] == "planned"
```

Run: `pytest tests/test_cli/test_loop_workspace_cmd.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/cli/loop_workspace_cmd.py src/loopdesk/cli/main.py tests/test_cli/test_loop_workspace_cmd.py
git commit -m "feat(cli): add loop workspace init and show commands"
```

---

### Task 6: Add loop workspace RPC surface for gateway clients

**Files:**
- Create: `src/loopdesk/gateway/rpc_loop_workspace.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_rpc_loop_workspace_create_and_get(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)
    ctx = RpcContext(conn_id="test", loop_workspace_service=service)

    created = await _handle_loop_workspace_create(
        {"path": str(tmp_path), "intent": "Ship loop workspace CLI."},
        ctx,
    )
    fetched = await _handle_loop_workspace_get({"loop_id": created["loop_id"]}, ctx)

    assert fetched["status"] == "planned"
    assert fetched["intent"] == "Ship loop workspace CLI."
```

Run: `pytest tests/test_gateway/test_rpc_loop_workspace.py::test_rpc_loop_workspace_create_and_get -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Write minimal implementation**

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loopdesk.gateway.rpc import RpcContext, _d
from loopdesk.loop_workspace.helpers import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.schema import LoopWorkspaceState


RpcContext.__annotations__["loop_workspace_service"] = LoopWorkspaceService | None


@_d.method("loopWorkspace.create", scope="operator.write")
async def _handle_loop_workspace_create(params: dict[str, Any] | None, ctx: RpcContext) -> dict[str, Any]:
    service = _resolve_service(ctx)
    path = Path((params or {}).get("path") or ".")
    state = await service.create_state(intent=str((params or {}).get("intent") or ""))
    return state.to_dict()


@_d.method("loopWorkspace.get", scope="operator.read")
async def _handle_loop_workspace_get(params: dict[str, Any] | None, ctx: RpcContext) -> dict[str, Any]:
    service = _resolve_service(ctx)
    loop_id = str((params or {}).get("loop_id") or "")
    return (await service.get_state(loop_id)).to_dict()


def _resolve_service(ctx: RpcContext) -> LoopWorkspaceService:
    service = getattr(ctx, "loop_workspace_service", None)
    if service is None:
        raise RuntimeError("loop_workspace_service is not configured")
    return service
```

**Step 3: Add RPC tests**

```python
def test_create_requires_intent() -> None:
    with pytest.raises(RpcHandlerError):
        asyncio.run(_handle_loop_workspace_create({"path": "/tmp"}, RpcContext(conn_id="test")))
```

Run: `pytest tests/test_gateway/test_rpc_loop_workspace.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/gateway/rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace.py
git commit -m "feat(gateway): add loop workspace RPC methods"
```

---

### Task 7: Add loop workspace web UI views and static assets

**Files:**
- Create: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Create: `src/loopdesk/gateway/static/css/views/loop_workspace.css`
- Modify: `src/loopdesk/gateway/control_ui.py:1-40`
- Test: `tests/test_gateway/test_loop_workspace_view_static.py`

**Step 1: Write the failing test**

```python
def test_loop_workspace_view_serves_js_and_css(client: TestClient) -> None:
    js_response = client.get("/control/static/js/views/loop_workspace.js")
    css_response = client.get("/control/static/css/views/loop_workspace.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert b"loop-workspace" in js_response.content
```

Run: `pytest tests/test_gateway/test_loop_workspace_view_static.py::test_loop_workspace_view_serves_js_and_css -v`
Expected: FAIL with missing file or 404

**Step 2: Write minimal implementation**

Create `loop_workspace.js`:

```javascript
window.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("loop-workspace-root");
  if (!root) return;

  const state = { intent: "", status: "unknown" };
  const intentField = root.querySelector("[data-loop-field=intent]");
  const statusField = root.querySelector("[data-loop-field=status]");
  const createButton = root.querySelector("[data-loop-action=create]");
  const refreshButton = root.querySelector("[data-loop-action=refresh]");

  async function loadLoopState() {
    const response = await rpc("loopWorkspace.get", {});
    state.intent = response.intent || "";
    state.status = response.status || "unknown";
    if (intentField) intentField.textContent = state.intent;
    if (statusField) statusField.textContent = state.status;
  }

  if (createButton) {
    createButton.addEventListener("click", async () => {
      const path = root.querySelector("[data-loop-path]")?.value || ".";
      const intent = root.querySelector("[data-loop-intent]")?.value || "";
      await rpc("loopWorkspace.create", { path, intent });
      await loadLoopState();
    });
  }

  if (refreshButton) {
    refreshButton.addEventListener("click", loadLoopState);
  }

  loadLoopState();
});
```

Create `loop_workspace.css`:

```css
.loop-workspace-shell {
  display: grid;
  gap: 12px;
}
.loop-workspace-shell .field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.loop-workspace-shell input {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}
```

Register the view in `src/loopdesk/gateway/control_ui.py` alongside existing view imports:

```python
from loopdesk.gateway.static.js.views import loop_workspace as loop_workspace_view  # noqa: E402
```

**Step 3: Add static tests**

```python
def test_loop_workspace_view_requires_root_element() -> None:
    html = client.get("/control/").text
    assert "loop-workspace-root" in html
```

Run: `pytest tests/test_gateway/test_loop_workspace_view_static.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/gateway/static/js/views/loop_workspace.js src/loopdesk/gateway/static/css/views/loop_workspace.css src/loopdesk/gateway/control_ui.py tests/test_gateway/test_loop_workspace_view_static.py
git commit -m "feat(ui): add loop workspace control view"
```

---

### Task 8: Add cross-tool adapter interfaces and a local CLI bridge

**Files:**
- Create: `src/loopdesk/loop_workspace/adapters.py`
- Create: `src/loopdesk/loop_workspace/cli_bridge.py`
- Test: `tests/test_loop_workspace/test_adapters.py`
- Test: `tests/test_loop_workspace/test_cli_bridge.py`

**Step 1: Write the failing test**

```python
def test_cli_bridge_creates_tool_context_from_loop_state(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)
    state = asyncio.run(
        service.create_state(
            intent="Implement cross-tool loop bridge.",
            tags=["codex", "claude-code"],
            worktree_path=tmp_path / "wt",
        )
    )
    bridge = CliToolBridge(service)

    context = bridge.build_tool_context(state.loop_id, tool="claude-code")

    assert context["loop_id"] == state.loop_id
    assert context["workspace_root"] == str(tmp_path)
    assert context["active_tool"] == "claude-code"
    assert context["worktree_path"] == str(tmp_path / "wt")
    assert "memory_search" in context["preloaded_context"]
```

Run: `pytest tests/test_loop_workspace/test_adapters.py tests/test_loop_workspace/test_cli_bridge.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Write minimal implementation**

`src/loopdesk/loop_workspace/adapters.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loopdesk.loop_workspace.schema import LoopWorkspaceState


@dataclass(frozen=True)
class ToolContext:
    loop_id: str
    workspace_root: str
    active_tool: str
    worktree_path: str
    memory_queries: list[str]
    skills: list[str]
    artifacts: list[dict[str, Any]]


class CrossToolAdapter:
    def __init__(self, tool: str) -> None:
        self.tool = tool

    def build_context(self, state: LoopWorkspaceState) -> ToolContext:
        return ToolContext(
            loop_id=state.loop_id or "",
            workspace_root=str(state.workspace_root),
            active_tool=self.tool,
            worktree_path=state.preferences.get("worktree_path", ""),
            memory_queries=[state.intent, *state.tags],
            skills=list(state.tags),
            artifacts=list(state.artifacts),
        )
```

`src/loopdesk/loop_workspace/cli_bridge.py`:

```python
from __future__ import annotations

from typing import Any

from loopdesk.loop_workspace.adapters import CrossToolAdapter, ToolContext
from loopdesk.loop_workspace.schema import LoopWorkspaceState


class CliToolBridge:
    def __init__(self, service: Any) -> None:
        self.service = service

    async def load_state(self, loop_id: str) -> LoopWorkspaceState:
        return await self.service.get_state(loop_id)

    def build_tool_context(self, loop_id: str, tool: str) -> dict[str, Any]:
        state = self.service._states[loop_id]
        context = CrossToolAdapter(tool=tool).build_context(state)
        return {
            "loop_id": context.loop_id,
            "workspace_root": context.workspace_root,
            "active_tool": context.active_tool,
            "worktree_path": context.worktree_path,
            "preloaded_context": {
                "memory_search": context.memory_queries,
                "skills": context.skills,
                "artifacts": context.artifacts,
            },
        }
```

**Step 3: Add adapter/bridge tests**

```python
def test_adapter_uses_tags_as_skill_hints(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)
    state = asyncio.run(service.create_state(intent="Draft docs.", tags=["docs", "release-note"]))
    context = CrossToolAdapter(tool="codex").build_context(state)

    assert context.skills == ["docs", "release-note"]
    assert context.memory_queries == ["Draft docs.", "docs", "release-note"]
```

Run: `pytest tests/test_loop_workspace/test_adapters.py tests/test_loop_workspace/test_cli_bridge.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/loopdesk/loop_workspace/adapters.py src/loopdesk/loop_workspace/cli_bridge.py tests/test_loop_workspace/test_adapters.py tests/test_loop_workspace/test_cli_bridge.py
git commit -m "feat(loop_workspace): add cross-tool adapter interface and CLI bridge"
```

---

### Task 9: Add loop workspace integration tests for developer scenarios

**Files:**
- Create: `tests/test_loop_workspace_integration/test_developer_scenarios.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_cross_tool_handoff_scenario_preserves_loop_context(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)
    bridge = CliToolBridge(service)

    state = await service.create_state(
        intent="Design API contract, then implement frontend.",
        tags=["claude-code", "codex"],
        worktree_path=tmp_path / "wt",
    )
    await service.update_state(
        state.loop_id,
        status=LoopWorkspaceStatus.ACTIVE,
        active_tool="claude-code",
        last_result="API contract drafted.",
    )
    claude_context = bridge.build_tool_context(state.loop_id, tool="claude-code")
    codex_context = bridge.build_tool_context(state.loop_id, tool="codex")

    assert codex_context["workspace_root"] == str(tmp_path)
    assert codex_context["active_tool"] == "codex"
    assert codex_context["preloaded_context"]["memory_search"] == ["Design API contract, then implement frontend.", "claude-code", "codex"]


@pytest.mark.asyncio
async def test_repetitive_loop_automation_scenario_writes_run_log(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)

    state = await service.create_state(intent="Daily dependency review.", tags=["automation", "review"])
    await service.update_state(
        state.loop_id,
        status=LoopWorkspaceStatus.COMPLETED,
        last_tool="loop-engine",
        last_result="Reviewed 12 dependencies; 2 updates proposed.",
        lessons=[{"lesson": "Prefer patch-only automation for review loops."}],
    )

    payload = json.loads(layout.state_file.read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert payload["last_tool"] == "loop-engine"
    assert payload["lessons"][0]["lesson"] == "Prefer patch-only automation for review loops."
```

Run: `pytest tests/test_loop_workspace_integration/test_developer_scenarios.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 2: Run the scenario tests after prior tasks are merged**

Run: `pytest tests/test_loop_workspace_integration/test_developer_scenarios.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_loop_workspace_integration/test_developer_scenarios.py
git commit -m "test(loop_workspace): add cross-tool and automation scenario tests"
```

---

### Task 10: Run focused verification and update docs checklist

**Step 1: Run focused verification**

Run: `pytest tests/test_loop_workspace tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_loop_workspace_integration/test_developer_scenarios.py`
Expected: all selected tests pass

Run: `pytest -m "not llm and not llm_smoke and not llm_costly and not llm_tools and not llm_embedding and not llm_reasoning"`
Expected: existing suite still passes

**Step 2: Update docs checklist**

- Add `v0.1 loop workspace CLI` to `/Users/freecisco_yan/Documents/trae_projects/savus/docs/features/core-feature-list.md:1`
- Add loop workspace adapter note to `/Users/freecisco_yan/Documents/trae_projects/savus/docs/architecture/personal-loop-workspace.md:1`
- Add loop workspace scenario note to `/Users/freecisco_yan/Documents/trae_projects/savus/docs/prd/personal-loop-workspace.md:1`

**Step 3: Final check**

Run: `rg "loop workspace|LOOP-STATE|loopWorkspace" docs src tests`
Expected: only intended v0.1 surfaces are present

**Step 4: Commit**

```bash
git add docs/features/core-feature-list.md docs/architecture/personal-loop-workspace.md docs/prd/personal-loop-workspace.md
git commit -m "docs: align product docs with v0.1 loop workspace plan"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-07-07-personal-loop-workspace.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?

If Subagent-Driven chosen:
- REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

If Parallel Session chosen:
- REQUIRED SUB-SKILL: Use superpowers:executing-plans
- Open new session in worktree
- Fresh session with executing-plans

## Assumptions
- `git` is installed and the project repo supports `git worktree`.
- Existing gateway/session/memory/skill surfaces are reused instead of rebuilt.
- ACP-first tool adapters are not required for v0.1 launch; MCP-first plus a generic CLI bridge is enough.
- Tutti/WeSight/Multica external verification remains incomplete; differentiation is based on current public signals plus internal repo review.
