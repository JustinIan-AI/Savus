# LoopDesk v0.1 Gap Closure Plan

> Date: 2026-07-10
> Status: completed
> Owner: Product / Engineering / QA
> Prerequisite: `docs/plans/2026-07-09-v01-gap-implementation-plan.md` feature skeleton is mostly on disk; this plan closes the remaining boot/behavior blockers before full front-back integration.

## 1. Goal

- Close the last gap between "LoopDesk v0.1 code exists" and "v0.1 is executable and sign-off ready."
- Deliver a concrete implementation sequence for the remaining blockers: RPC registration boot gap, engine start/stop state leakage, static view collection blocker, stale acceptance/sign-off docs, and full pytest evidence capture.
- Make the gap count concrete: before this plan, frontend panel wiring was mostly implemented but 5 new gateway test files could not execute; after this plan, the new `loop_workspace.*` surface can be verified through normal pytest collection.

## 2. Current Baseline

### 2.1 Completed
- `LOOP-STATE.json`, layout, service, memory, skills, worktree, templates, CLI, and many backend RPC handlers are implemented.
- Interactive local Web UI panels for run log detail, replay pack, adapter tools, and engine controls are wired in `src/loopdesk/gateway/static/js/views/loop_workspace.js`.
- Engine state machine, runner, budget/kill-switch enforcement, fake MCP adapter round-trip, and integration coverage are in place.
- F1 API behavior fixes for approval respond and run-log-cost propagation were intended, but F1 tests could not execute because of a later-discovered boot-time registry issue.

### 2.2 Blocked
- Normal `pytest` collection for new `tests/test_gateway/test_rpc_loop_workspace_*.py` files returned `None` for every handler until `loopdesk.gateway.rpc_loop_workspace` was imported at boot.
- `tests/test_gateway/test_loop_workspace_view_static.py` failed collection because `LOOP_WORKSPACE_VIEW_FILES` was missing from `loopdesk.gateway.control_ui`.
- Engine start did not initialize `current_iteration` and did not write a start run-log entry; engine stop did not write a stop run-log entry.
- Acceptance checklist and sign-off still show Pending because F3-F6 evidence was based on direct scripts rather than full pytest.

## 3. Remaining Gaps

| ID | Gap | Impact |
| --- | --- | --- |
| G1 | RPC boot registration gap | All new `loop_workspace.*` endpoints silently returned `None` in tests. |
| G2 | Static view collection blocker | `pytest tests/test_gateway -k loop_workspace` stopped on an `ImportError`. |
| G3 | Engine lifecycle run-log gap | Frontend status panel could show stale state; audit trail was incomplete. |
| G4 | Acceptance/sign-off drift | Docs still said F3-F6 were pending full pytest recovery. |
| G5 | Test harness event-loop fixture gap | New gateway tests could hang in this environment without a nested-loop helper. |

## 4. Implementation Plan

### Task 1: Restore loop workspace RPC boot registration
**Files:**
- Edit: `src/loopdesk/gateway/rpc/__init__.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_engine.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_replay.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_adapters.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py`

**Step 1: Root cause**
- `validate_classification()` locked the registry before `rpc_loop_workspace` was imported, so newly added product methods were invisible to dispatcher lookups.

**Step 2: Fix**
- Import `loopdesk.gateway.rpc_loop_workspace` alongside the other sibling RPC modules before classification runs.

**Step 3: Verify**
```bash
python -m pytest tests/test_gateway/test_rpc_loop_workspace_engine.py tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py tests/test_gateway/test_rpc_loop_workspace_replay.py tests/test_gateway/test_rpc_loop_workspace_adapters.py tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py -q
```

### Task 2: Fix static view collection blocker
**Files:**
- Edit: `src/loopdesk/gateway/control_ui.py`
- Test: `tests/test_gateway/test_loop_workspace_view_static.py`

**Step 1: Root cause**
- The LoopDesk view assets exist in static JS/CSS and HTML, but `control_ui.py` did not export the `LOOP_WORKSPACE_VIEW_FILES` mapping expected by the view test.

**Step 2: Fix**
- Add a small `LOOP_WORKSPACE_VIEW_FILES` constant mapping `js` and `css` paths for the LoopDesk workbench view.

**Step 3: Verify**
```bash
python -m pytest tests/test_gateway/test_loop_workspace_view_static.py -q
```

### Task 3: Add nested event-loop fixtures for new gateway loop workspace tests
**Files:**
- Edit: `tests/test_gateway/test_rpc_loop_workspace_engine.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_replay.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_adapters.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_approvals.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_cost.py`
- Edit: `tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py`

**Step 1: Root cause**
- `RpcRegistry.handle` is synchronous, but this environment's pytest/event-loop stack can leave a running loop on the stack; some gateway tests therefore hang instead of completing.

**Step 2: Fix**
- Add an autouse fixture that monkeypatches `get_dispatcher().handle` to run dispatcher coroutines through a nested event loop fallback.

**Step 3: Verify**
```bash
python -m pytest tests/test_gateway -k loop_workspace -q
```

### Task 4: Improve engine lifecycle run-log behavior
**Files:**
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py`

**Step 1: Fix**
- Initialize `current_iteration=0` in `loop_workspace.engine.start`.
- Write a `loop-engine` run-log entry on engine start.
- Write a `loop-engine` run-log entry on engine stop so frontend history and replay pack remain coherent.

**Step 2: Verify**
```bash
python -m pytest tests/test_gateway/test_rpc_loop_workspace_engine.py tests/test_gateway/test_rpc_loop_workspace_replay.py -q
```

### Task 5: Reconcile stale acceptance docs and capture final pytest evidence
**Files:**
- Edit: `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
- Edit: `docs/acceptance/loopdesk-v0.1-signoff-report.md`
- Edit: `docs/plans/2026-07-10-v01-frontend-integration-gap-report.md`

**Step 1: Update docs**
- Mark panel/replay/adapter/engine coverage as Pass once pytest evidence is collected.
- Remove "pending full pytest recovery" language from sign-off roles.
- Record the actual blocker history: boot registration gap, static view constant gap, and event-loop fixture gap.

**Step 2: Final gate command**
```bash
python -m pytest tests/test_loop_workspace tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_loop_workspace_integration/test_developer_scenarios.py tests/test_gateway/test_rpc_loop_workspace_adapters.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_engine.py tests/test_gateway/test_rpc_loop_workspace_extended.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_replay.py tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py tests/test_gateway/test_rpc_loop_workspace_skills.py tests/test_loop_workspace_integration/test_workspace_first_flow.py -q
```

## 5. Stop Condition

This plan is complete when:
- `pytest tests/test_gateway -k loop_workspace` no longer stops on import/registry errors.
- All targeted loop workspace gateway files in Task 1 pass.
- Engine start/stop produce consistent state and run-log history.
- Acceptance checklist and sign-off reflect actual pytest evidence instead of "pending recovery."
