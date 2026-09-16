# LoopDesk v0.1 Gap Implementation Plan

> Date: 2026-07-09
> Status: ready for review
> Owner: Product / Engineering / QA
> Prerequisite: `docs/plans/2026-07-07-personal-loop-workspace.md` Task 1-10 (data layer skeleton — done)
> Goal: close the front-back integration gap and deliver v0.1 PRD launch criteria with FDD + TDD discipline

---

## 1. Product Goal

### 1.1 Feature Goal
- 让独立开发者能在本地 LoopDesk 工作台里连续查看当前工作、运行日志、审批、成本、memory、skills 和 worktree，而不必在多个 CLI/Web UI 之间手动拼装上下文。
- 补齐 v0.1 仍缺失的 backend behavior：Loop Engine、Cross-Tool Adapter、Budget Enforcement、Run Log/Replay、Docs/Tests/Release gates。
- 让前后端联调基于稳定 API contract 推进，而不是基于 mock 或口头约定。

### 1.2 Scope In
- `loop_workspace` 现有 29 个 RPC 的联调修复与交互面板接线
- Loop Engine 最小可用状态机 / runner / 5 个 RPC
- 至少一个本地 coding workflow 的 MCP round-trip
- Budget Enforcement runtime（budget exceeded / kill switch / denylist / repeated failure）
- Run Log detail / replay pack / compaction workflow
- 定向集成测试、acceptance checklist、release notes

### 1.3 Scope Out
- team collaboration、cloud sync、marketplace skills、heavy desktop GUI
- ACP 作为 v0.1 公开主路径
- legacy `session` / `workspace-state.json` / channel-first 叙事继续作为 runtime 兼容，不作为 v0.1 产品表面扩张

### 1.4 Affected Files
- `src/loopdesk/gateway/rpc_loop_workspace.py`
- `src/loopdesk/loop_workspace/service.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/memory.py`
- `src/loopdesk/loop_workspace/skills.py`
- `src/loopdesk/loop_workspace/mcp.py`
- `src/loopdesk/loop_workspace/engine/state_machine.py`
- `src/loopdesk/loop_workspace/engine/runner.py`
- `src/loopdesk/loop_workspace/adapters/mcp_client.py`
- `src/loopdesk/loop_workspace/adapters/event_translator.py`
- `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- `src/loopdesk/gateway/static/css/views/loop_workspace.css`
- `tests/test_gateway/test_rpc_loop_workspace*.py`
- `tests/test_loop_workspace/test_engine_*.py`
- `tests/test_loop_workspace/test_mcp_client.py`
- `tests/test_loop_workspace/test_event_translator.py`
- `tests/test_loop_workspace/test_budget_enforcement.py`
- `tests/test_loop_workspace_integration/test_workspace_first_flow.py`
- `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
- `docs/releases/loopdesk-v0.1.md`

### 1.5 Loop Engineering Run Format
- Triage：按联调阻塞度排序；先修 blocking API，再补核心能力，最后做前端面板与 release gates
- Maker：每个任务先写 failing test，再最小实现，再跑定向测试
- Checker：运行本任务定向 pytest；确认无回归后再进入下一任务
- Escalation：若 scope 膨胀或 legacy surface 泄露，停止实现并更新 docs/plans
- Run log：在 plan 中记录 started task / result / next step / risk note
- Stop condition：feature acceptance criteria 满足，且无未解决的 public-surface leak

### 1.6 Acceptance Criteria
- 联调前 API 阻塞数为 0
- LoopDesk 工作台可交互完成：查看 workspace、更新 intent/status/template、resume、export、memory、skills、approvals、cost、worktree、run log
- Loop Engine 至少跑通一个 triage→maker→checker→completed 或 escalation 场景
- 至少一个本地 coding workflow 通过 MCP adapter 完成 round-trip
- budget exceeded / kill switch / denylist / ambiguous escalation 各有定向测试
- 定向集成测试通过
- docs/acceptance/release notes 已同步

### 1.7 Rollback Criteria
- 若修复 approval/cost API 会破坏现有 schema 字段兼容性，则回滚到只新增返回字段，不删既有字段
- 若 Loop Engine 范围膨胀到云任务/多用户，则回滚到本地最小 runner
- 若前端 panel 导致 legacy channel 入口成为主路径，则回滚并收口导航
- 若 MCP adapter 依赖外部工具导致 CI 不稳定，则回滚到 fake MCP server 集成

---

## 2. Current Baseline

### 2.1 Already Implemented
- `LOOP-STATE.json` schema, serialization, layout, service, repository
- CLI: `init`, `show`, `list`, `update`, `resume`, `export`, `worktree`, `cost`, `kill-switch`, `denylist`
- MCP stdio: `get_context_pack`, `list_templates`, `read_template`, `run_local_command`
- Gateway RPC: 29 `loop_workspace.*` methods registered
- Web UI static shell: `loop_workspace.js/css` + legacy approvals/skills views
- Memory: `DurableMemoryIndex` append/search/compact/resume_pack
- Skills: `LoopWorkspaceSkillRegistry` list/inspect/audit

### 2.2 Verified Test Baseline
- Loop workspace tests: `tests/test_loop_workspace/test_schema.py`, `test_layout.py`, `test_service.py`, `test_memory.py`, `test_skills.py`, `test_worktree.py`
- Integration tests: `tests/test_loop_workspace_integration/test_developer_scenarios.py`
- CLI tests: `tests/test_cli/test_loop_workspace_cmd.py`
- Gateway RPC tests: `tests/test_gateway/test_rpc_loop_workspace.py`, `test_rpc_loop_workspace_memory.py`, `test_rpc_loop_workspace_skills.py`, `test_rpc_loop_workspace_approvals.py`, `test_rpc_loop_workspace_cost.py`, `test_rpc_loop_workspace_extended.py`

Current verification result:
```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_layout.py tests/test_loop_workspace/test_service.py tests/test_loop_workspace/test_memory.py tests/test_loop_workspace/test_skills.py tests/test_loop_workspace/test_worktree.py tests/test_loop_workspace_integration/test_developer_scenarios.py tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```

Result: `32 passed, 2 failed`
- Failure 1: `tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond`
- Failure 2: `tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history`

### 2.3 Front-Back Integration Gap
- `src/loopdesk/gateway/static/js/views/loop_workspace.js` currently calls only:
  - `loop_workspace.get`
  - `loop_workspace.export`
  - `loop_workspace.resume`
- Missing front-end wiring for:
  - `loop_workspace.update`
  - `loop_workspace.list`
  - `loop_workspace.templates.apply`
  - `loop_workspace.memory.*`
  - `loop_workspace.skills.*`
  - `loop_workspace.approvals.list` / `loop_workspace.approval.respond`
  - `loop_workspace.cost.set_budget` / `loop_workspace.cost.history`
  - `loop_workspace.set_kill_switch` / `loop_workspace.set_denylist`
  - `loop_workspace.run_log.list`
  - `loop_workspace.worktree.create` / `loop_workspace.worktree.list` / `loop_workspace.worktree.remove`
  - `loop_workspace.engine.*`

### 2.4 v0.1 Gap Summary
- Loop Engine: zero code
- Cross-Tool Adapter real handoff: zero round-trip implementation
- Budget Enforcement runtime: schema exists, no active enforcement
- Run Log / Replay / Compaction user workflow: partial
- Web UI interactive panels: static shell only
- 2 pre-integration API bugs blocking frontend wiring

---

## 3. Feature Breakdown

### Feature F1: Fix Pre-Integration Blocking APIs
#### Feature Goal
- 关闭联调前 2 个 backend RPC 行为 bug，让前端可以基于真实 payload 继续接线。
#### Scope In
- `loop_workspace.approval.respond` 返回值修复
- `loop_workspace.cost.history` 持久化修复
- 定向测试通过
#### Scope Out
- 不新增 approval/cost domain behavior
- 不改动 schema 字段名和现有持久化格式
#### Affected Files
- `src/loopdesk/gateway/rpc_loop_workspace.py`
- `src/loopdesk/loop_workspace/service.py`
- `tests/test_gateway/test_rpc_loop_workspace_approvals.py`
- `tests/test_gateway/test_rpc_loop_workspace_cost.py`
#### Loop Engineering Run Format
- Triage：先修 approval.respond，再修 cost.history
- Maker：每个任务先写 failing test，再最小实现
- Checker：运行定向 pytest
- Escalation：若发现 schema 兼容性问题，停止并更新 risk-handling-plan
- Run log：记录失败原因、修复结果、回归检查结果
- Stop condition：2 个阻塞测试全部 passed，且无回归
#### Acceptance Criteria
- `tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond` passed
- `tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history` passed
- `tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py::test_rpc_loop_workspace_approval_respond_returns_updated_state` passed
- `tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py::test_rpc_loop_workspace_cost_history_persists_cost_from_run_log` passed
- `pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q` passed

##### Verification Evidence
- `python -m py_compile` on touched Python files exits `0`.
- Direct script executes `tests.test_gateway.test_rpc_loop_workspace_f1_fixes.run_f1_regression_checks()` without import errors.
- Direct script exercises approval/cost/replay/compact/detail/adapter/engine routes and confirms expected payload shapes.

##### Known Verification Blocker
- This environment currently blocks normal `pytest` invocation at test collection for gateway test files. Use the regression runner in `tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py` or the internal script in that file to verify F1 behavior until pytest collection is restored.
#### Rollback Criteria
- 若修复破坏现有 `LOOP-STATE.json` 兼容性，回滚到只新增字段/返回结构

---

#### Task F1-T1: Fix `loop_workspace.approval.respond`
##### Step 1: Write the failing test
`tests/test_gateway/test_rpc_loop_workspace_approvals.py`
```python
def test_rpc_loop_workspace_approval_respond_returns_state(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    dispatcher.handle(
        "loop_workspace.record_approval",
        {"root": root, "id": "approval-1", "status": "pending", "payload": {"action": "edit"}},
        _RpcContext(),
    )

    payload = dispatcher.handle(
        "loop_workspace.approval.respond",
        {"root": root, "id": "approval-1", "status": "denied", "payload": {"note": "nope"}},
        _RpcContext(),
    )
    assert payload is not None
    assert payload["approvals"][0]["status"] == "denied"
    assert payload["current_work_id"] is None
```

Run:
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond_returns_state -v
```
Expected: `FAILED` with `TypeError` or assertion failure

##### Step 2: Write minimal implementation
`src/loopdesk/gateway/rpc_loop_workspace.py`
```python
@dispatcher.method("loop_workspace.approval.respond", scope="operator.write")
async def loop_workspace_approval_respond(params: dict[str, object], context) -> dict[str, object]:
    service = _loop_workspace_service_from_params(params)
    service.record_approval(
        {
            "id": params["id"],
            "status": params["status"],
            "payload": params.get("payload", {}),
            "updated_at": _utc_now(),
        }
    )
    return service.current_state()
```

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_approvals.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```
Expected: `approval_respond` passed, no regression

---

#### Task F1-T2: Fix `loop_workspace.cost.history`
##### Step 1: Write the failing test
`tests/test_gateway/test_rpc_loop_workspace_cost.py`
```python
def test_rpc_loop_workspace_cost_history_persists_from_run_log(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    dispatcher.handle(
        "loop_workspace.record_run_log",
        {
            "root": root,
            "source": "loop",
            "workId": "work-1",
            "status": "active",
            "summary": "Did work.",
            "cost": {"cost_usd": 0.05, "model": "mock-model"},
        },
        _RpcContext(),
    )

    payload = dispatcher.handle(
        "loop_workspace.cost.history",
        {"root": root, "limit": 10},
        _RpcContext(),
    )
    assert payload["total"] == 1
    assert payload["history"][0]["cost_usd"] == 0.05
```

Run:
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history_persists_from_run_log -v
```
Expected: `FAILED` with `assert 0 == 1`

##### Step 2: Write minimal implementation
`src/loopdesk/loop_workspace/service.py`
```python
def record_run_log(self, run_log: dict[str, object]) -> dict[str, object]:
    state = self._repository.read()
    entry = dict(run_log)
    if run_log.get("cost"):
        entry["cost"] = run_log["cost"]
    state.append_run_log(entry)
    if run_log.get("cost"):
        state.record_cost(run_log["cost"])
    self._repository.write(state)
    return self.current_state()
```

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_cost.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```
Expected: `cost_history` passed, no regression

---

### Feature F2: LoopDesk Workbench Interactive Panels
#### Feature Goal
- 把 LoopDesk Web UI 从静态观察壳变成可交互工作台，覆盖 v0.1 PRD 要求的 continuous workflow surface。
#### Scope In
- workspace header + state editing
- cost + safety panel
- approval panel
- memory panel
- skills panel
- worktree panel
- run log detail panel
- loop engine panel
#### Scope Out
- legacy channel-first dashboard 作为兼容保留，不作为主入口
- heavy desktop GUI、team workspace、multi-user auth
#### Affected Files
- `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- `src/loopdesk/gateway/static/css/views/loop_workspace.css`
- `tests/test_gateway/test_loop_workspace_panels.py`
#### Loop Engineering Run Format
- Triage：先接已实现 RPC，再补 engine panel
- Maker：每个 panel 用 failing test 约束最小实现
- Checker：定向 panel tests + 定向 RPC tests
- Escalation：若前端发现需要新 RPC，回到 backend plan 追加 task
- Run log：记录 panel 覆盖率、未接线 RPC、回归
- Stop condition：8 个 panel 最小可用版本完成且无公开 surface 泄露
#### Acceptance Criteria
- LoopDesk 工作台至少支持以下交互：
  - 选择/刷新 workspace
  - 编辑 intent / status / template
  - resume / export
  - memory append/search/compact/resume_pack
  - skills list/inspect/audit
  - approvals list/respond
  - cost set_budget/history; kill switch; denylist
  - worktree create/list/remove
  - run log list/detail
  - engine start/stop/status/step/set_stop_condition
- 所有用户操作都有 loading/error toast
- 不使用 legacy approvals/skills 页面作为主流程
#### Rollback Criteria
- 若 panel 接线导致浏览器 bundle/静态资源异常，回滚到只保留 minimal interactive shell
- 若命名泄露 legacy channel/session，立即回滚文案与导航

---

#### Task F2-T1: Workspace Header + State Editing
##### Step 1: Write the failing test
`tests/test_gateway/test_loop_workspace_panels.py`
```python
def test_loop_workspace_panel_header_edits_state_via_rpc(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    # UI calls loop_workspace.create/get/list/update/templates.apply
    # ... simulate panel interactions ...
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_header_edits_state_via_rpc -v
```
Expected: `FAILED` (test not implemented yet)

##### Step 2: Write minimal implementation
- `loop_workspace.js`:
  - workspace selector dropdown
  - inline intent/status/template editor
  - call `loop_workspace.list/get/update/templates.apply`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T2: Cost + Safety Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_cost_and_safety_controls(tmp_path: Path) -> None:
    # set budget -> history shows event -> kill switch updates state
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_cost_and_safety_controls -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.cost.set_budget`
- wire `loop_workspace.cost.history`
- wire `loop_workspace.set_kill_switch`
- wire `loop_workspace.set_denylist`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T3: Approval Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_approval_respond_refreshes_without_navigation(tmp_path: Path) -> None:
    # record approval -> respond -> panel refreshes
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_approval_respond_refreshes_without_navigation -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.approvals.list`
- wire `loop_workspace.approval.respond`
- keep approve/deny in-panel

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T4: Memory Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_memory_append_search_compact_and_resume_pack(tmp_path: Path) -> None:
    # append -> search -> compact -> resume_pack
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_memory_append_search_compact_and_resume_pack -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.memory.append`
- wire `loop_workspace.memory.search`
- wire `loop_workspace.memory.compact`
- wire `loop_workspace.memory.resume_pack`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T5: Skills Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_skills_list_inspect_and_audit(tmp_path: Path) -> None:
    # skills.list -> inspect -> audit badge
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_skills_list_inspect_and_audit -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.skills.list`
- wire `loop_workspace.skills.inspect`
- wire `loop_workspace.skills.audit`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T6: Worktree Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_worktree_create_list_and_remove(tmp_path: Path) -> None:
    # create -> list -> remove
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_worktree_create_list_and_remove -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.worktree.create`
- wire `loop_workspace.worktree.list`
- wire `loop_workspace.worktree.remove`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T7: Run Log Detail Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_run_log_list_and_detail(tmp_path: Path) -> None:
    # record run log -> list -> detail
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_run_log_list_and_detail -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.run_log.list`
- add expandable detail view for cost/approval association

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

#### Task F2-T8: Loop Engine Panel
##### Step 1: Write the failing test
```python
def test_loop_workspace_panel_engine_start_step_stop_and_status(tmp_path: Path) -> None:
    # start -> step -> stop -> status updates -> run log visible
```

Run:
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py::test_loop_workspace_panel_engine_start_step_stop_and_status -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire `loop_workspace.engine.status`
- wire `loop_workspace.engine.start`
- wire `loop_workspace.engine.stop`
- wire `loop_workspace.engine.step`
- wire `loop_workspace.engine.set_stop_condition`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

---

### Feature F3: Loop Engine Core
#### Status
- In progress as of 2026-07-10. State machine, runner, and engine RPC exist. Engine state is now persisted into `LOOP-STATE.json` and runner enforces budget/kill switch. Final direct verification and plan completion evidence are pending.
#### Feature Goal
- 实现 LoopDesk 核心差异化能力：triage/maker/checker/escalation/stop condition，并暴露为可调用的 RPC。
#### Scope In
- Loop Engine state machine
- Loop Engine runner
- 5 个 Loop Engine RPC endpoints
- 定向 backend tests
#### Scope Out
- 不直接接入 cloud scheduler
- v0.1 不实现复杂 LLM provider 编排，只提供 pluggable handler 骨架
#### Affected Files
- `src/loopdesk/loop_workspace/engine/state_machine.py`
- `src/loopdesk/loop_workspace/engine/runner.py`
- `src/loopdesk/gateway/rpc_loop_workspace.py`
- `tests/test_loop_workspace/test_engine_state_machine.py`
- `tests/test_loop_workspace/test_engine_runner.py`
- `tests/test_gateway/test_rpc_loop_workspace_engine.py`
#### Loop Engineering Run Format
- Triage：state machine 先行，runner 其次，RPC 最后
- Maker：每个模块先 failing test，再最小实现
- Checker：定向 engine tests + loop workspace tests
- Escalation：若 state machine 过度复杂，回滚到最小 triage/maker/checker 三态
- Run log：记录 phase transition、handler 调用、budget/denylist check
- Stop condition：至少一个完整 triage→maker→checker→completed 或 escalation 跑通
#### Acceptance Criteria
- state machine 支持 planned/triage/maker/checker/escalation/completed/failed/paused
- runner 支持 step/run/stop
- 5 个 RPC 注册并通过定向测试
- budget/kill switch/denylist 在 runner 中被检查
- 每个 phase transition 写结构化 run_log
#### Rollback Criteria
- 若 state machine 导致 schema 迁移问题，回滚到在 `LOOP-STATE.json` 中新增嵌套 `engine` 字段
- 若 runner 阻塞主线程，回滚到 async step-only 模式

---

#### Task F3-T1: Loop Engine State Machine
##### Step 1: Write the failing test
`tests/test_loop_workspace/test_engine_state_machine.py`
```python
def test_state_machine_allows_triage_to_maker_when_goal_is_concrete() -> None:
    state = LoopEngineState(phase=LoopPhase.triage, goal="Fix login bug")
    result = LoopEngineStateMachine.transition(state, decision="act")
    assert result.phase == LoopPhase.maker
```

Run:
```bash
pytest tests/test_loop_workspace/test_engine_state_machine.py::test_state_machine_allows_triage_to_maker_when_goal_is_concrete -v
```
Expected: `FAILED` (module not found)

##### Step 2: Write minimal implementation
- Create `src/loopdesk/loop_workspace/engine/state_machine.py`
- Implement `LoopPhase`, `LoopEngineState`, `LoopEngineStateMachine`

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace/test_engine_state_machine.py -v
```

---

#### Task F3-T2: Loop Engine Runner
##### Step 1: Write the failing test
`tests/test_loop_workspace/test_engine_runner.py`
```python
def test_runner_executes_one_step_and_records_run_log(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    runner = LoopEngineRunner(service)
    state = runner.step(LoopEngineState(phase=LoopPhase.triage, goal="X"))
    assert state.phase in {LoopPhase.maker, LoopPhase.escalation}
```

Run:
```bash
pytest tests/test_loop_workspace/test_engine_runner.py::test_runner_executes_one_step_and_records_run_log -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- Create `src/loopdesk/loop_workspace/engine/runner.py`
- Implement `LoopEngineRunner.step()` and `LoopEngineRunner.run()` with pluggable handlers

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace/test_engine_runner.py -v
```

---

#### Task F3-T3: Loop Engine RPC
##### Step 1: Write the failing test
`tests/test_gateway/test_rpc_loop_workspace_engine.py`
```python
def test_rpc_loop_workspace_engine_start_and_status(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    dispatcher = get_dispatcher()
    root = str(service.layout.root)

    start = dispatcher.handle("loop_workspace.engine.start", {"root": root, "goal": "X"}, _RpcContext())
    status = dispatcher.handle("loop_workspace.engine.status", {"root": root}, _RpcContext())
    assert start["phase"] == status["phase"]
```

Run:
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_engine.py::test_rpc_loop_workspace_engine_start_and_status -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- register `loop_workspace.engine.start/stop/status/step/set_stop_condition`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_engine.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py -q
```

---

### Feature F4: Cross-Tool Adapter
#### Status
- In progress as of 2026-07-10. `McpClient`, adapter round-trip, and `translate_inbound` are implemented. Fake MCP round-trip integration coverage is added. Final direct verification is pending.
#### Feature Goal
- 至少打通一个本地 coding workflow 的 MCP round-trip：LoopDesk -> tool -> workspace state。
#### Scope In
- MCP stdio client
- tool event -> workspace state translator
- 1 个 integration test
#### Scope Out
- cloud-hosted tool runtime
- vendor-specific protocol扩展
#### Affected Files
- `src/loopdesk/loop_workspace/adapters/mcp_client.py`
- `src/loopdesk/loop_workspace/adapters/event_translator.py`
- `src/loopdesk/loop_workspace/mcp.py`
- `tests/test_loop_workspace/test_mcp_client.py`
- `tests/test_loop_workspace/test_event_translator.py`
- `tests/test_loop_workspace_integration/test_cross_tool_handoff.py`
#### Loop Engineering Run Format
- Triage：先 translator，再 client，再 integration
- Maker：failing test -> minimal implementation
- Checker：定向 adapter tests + integration test
- Escalation：若外部工具不可控，回滚到 fake MCP server
- Run log：记录 handoff 事件、artifact、cost/approval 写回结果
- Stop condition：一个 round-trip integration test passed
#### Acceptance Criteria
- workspace -> context pack -> tool -> tool result -> run_log/artifact/memory 写回
- 至少一个本地 coding workflow 可以通过 CLI/Web UI 触发并观察到结果
#### Rollback Criteria
- 若 MCP stdio 不稳定，回滚到 process-level harness 测试，不阻塞 release

---

#### Task F4-T1: Tool Event Translator
##### Step 1: Write the failing test
`tests/test_loop_workspace/test_event_translator.py`
```python
def test_translator_writes_run_log_and_artifact() -> None:
    event = {"tool": "code_exec", "stdout": "ok", "artifact": "a.txt"}
    update = translate_inbound(event)
    assert update["run_log"][-1]["toolEvent"]["tool"] == "code_exec"
```

Run:
```bash
pytest tests/test_loop_workspace/test_event_translator.py::test_translator_writes_run_log_and_artifact -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- implement `translate_inbound` and `translate_outbound`

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace/test_event_translator.py -v
```

---

#### Task F4-T2: MCP Adapter Client
##### Step 1: Write the failing test
`tests/test_loop_workspace/test_mcp_client.py`
```python
def test_mcp_client_connect_and_call_tool() -> None:
    client = McpClient()
    client.connect("python", ["-m", "fake_server"])
    tools = client.list_tools()
    result = client.call_tool("echo", {"text": "hi"})
    assert result["ok"] is True
```

Run:
```bash
pytest tests/test_loop_workspace/test_mcp_client.py::test_mcp_client_connect_and_call_tool -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- implement stdio connect/initialize/list_tools/call_tool/disconnect

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace/test_mcp_client.py -v
```

---

#### Task F4-T3: Cross-Tool Handoff Integration Test
##### Step 1: Write the failing test
`tests/test_loop_workspace_integration/test_cross_tool_handoff.py`
```python
def test_workspace_to_tool_and_back_round_trip(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    # ... simulate handoff ...
    assert len(service.repository.read().run_log) > 0
```

Run:
```bash
pytest tests/test_loop_workspace_integration/test_cross_tool_handoff.py::test_workspace_to_tool_and_back_round_trip -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire adapter + translator + fake tool server

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace_integration/test_cross_tool_handoff.py -v
```

---

### Feature F5: Budget Enforcement and Run Log/Replay
#### Status
- In progress as of 2026-07-10. Runner now pauses on budget/kill switch, persists engine state, and existing run-log/replay/compaction endpoints remain. Final direct verification evidence is pending.
#### Feature Goal
- 让 budget、kill switch、denylist、repeated failure 在 backend 自动触发 report-only/paused/escalation，而不是只展示数字。
#### Scope In
- `cost_observatory.status` enforcement
- engine step 前置检查
- run log detail / replay pack / compaction
#### Scope Out
- cloud billing、team approval workflow
#### Affected Files
- `src/loopdesk/loop_workspace/service.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/engine/runner.py`
- `src/loopdesk/gateway/rpc_loop_workspace.py`
- `tests/test_loop_workspace/test_budget_enforcement.py`
- `tests/test_gateway/test_rpc_loop_workspace_replay.py`
- `tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py`
#### Loop Engineering Run Format
- Triage：先 enforcement，再 run log/replay
- Maker：failing test -> minimal guard logic
- Checker：定向 tests + regression tests
- Escalation：若 enforcement 与 existing cost schema 冲突，回滚到只新增 status
- Run log：记录 enforcement events、paused reason、recovery path
- Stop condition：至少 1 个 budget exceeded / kill switch / denylist 场景 passed
#### Acceptance Criteria
- budget exceeded -> paused + escalation reason
- kill switch -> paused
- denylist hit -> paused + approval queue
- repeated failure -> escalation
- run_log.detail 可展开单条记录
- replay.pack 可恢复上下文
- session.compact 保留关键 run log + memory
#### Rollback Criteria
- 若 enforcement 导致大量 existing run_log 不兼容，回滚到只对新 run_log 生效

---

#### Task F5-T1: Budget Enforcement Runtime
##### Step 1: Write the failing test
`tests/test_loop_workspace/test_budget_enforcement.py`
```python
def test_engine_pauses_when_budget_exceeded(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.record_cost({"cost_usd": 10.0, "budget_cap_usd": 1.0})
    # runner step should pause
```

Run:
```bash
pytest tests/test_loop_workspace/test_budget_enforcement.py::test_engine_pauses_when_budget_exceeded -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- add enforcement check in runner/service
- update `cost_observatory.status`

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace/test_budget_enforcement.py -v
```

---

#### Task F5-T2: Run Log / Replay / Compaction APIs
##### Step 1: Write the failing test
`tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py`
```python
def test_rpc_run_log_detail_returns_associated_cost_and_approval(tmp_path: Path) -> None:
    ...
```

Run:
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py::test_rpc_run_log_detail_returns_associated_cost_and_approval -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- add `loop_workspace.run_log.detail`
- add `loop_workspace.replay.pack`
- add `loop_workspace.session.compact`

##### Step 3: Run targeted verification
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py tests/test_gateway/test_rpc_loop_workspace_replay.py -v
```

---

### Feature F6: Integration and Release Gates
#### Status
- In progress as of 2026-07-10. Workspace-first integration test expanded with engine/adapter coverage; release docs updated. Direct verification and full gate evidence are pending.
#### Feature Goal
- 保证 v0.1 在功能、测试、文档、命名边界上都达到可发布状态。
#### Scope In
- 1 个定向集成测试
- 定向测试套件通过
- docs/acceptance/release notes 更新
#### Scope Out
- 额外的 marketing/website 内容
#### Affected Files
- `tests/test_loop_workspace_integration/test_workspace_first_flow.py`
- `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
- `docs/releases/loopdesk-v0.1.md`
- `docs/plans/2026-07-09-v01-gap-implementation-plan.md`
#### Loop Engineering Run Format
- Triage：先集成测试，再全量定向测试，再文档
- Maker：failing integration test -> minimal workflow -> docs
- Checker：定向 pytest + boundary grep
- Escalation：若 legacy surface 泄露，停止并回到 product/architecture docs
- Run log：记录集成结果、阻塞项、修复项
- Stop condition：集成测试 passed，定向测试 passed，docs synced
#### Acceptance Criteria
- `tests/test_loop_workspace_integration/test_workspace_first_flow.py` passed
- 定向测试套件 passed
- acceptance checklist 标记 Pass
- release notes 明确 v0.1 边界
- 无 legacy channel/session 作为 v0.1 主表面
#### Rollback Criteria
- 若集成测试依赖不稳定外部服务，回滚到本地 fake server

---

#### Task F6-T1: Workspace-First Integration Test
##### Step 1: Write the failing test
`tests/test_loop_workspace_integration/test_workspace_first_flow.py`
```python
def test_workspace_first_flow_from_init_to_engine_stop(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    # init -> engine start -> memory append -> approval respond -> worktree create -> engine stop
```

Run:
```bash
pytest tests/test_loop_workspace_integration/test_workspace_first_flow.py::test_workspace_first_flow_from_init_to_engine_stop -v
```
Expected: `FAILED`

##### Step 2: Write minimal implementation
- wire existing RPC + engine + adapter into one scenario

##### Step 3: Run targeted verification
```bash
pytest tests/test_loop_workspace_integration/test_workspace_first_flow.py -v
```

---

#### Task F6-T2: Full Targeted Test Pass
##### Verification
```bash
pytest tests/test_loop_workspace tests/test_loop_workspace_integration tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py -q
```
Expected: all passed

---

#### Task F6-T3: Documentation and Release Notes
##### Step 1: Update acceptance checklist
- mark new tests as Pass evidence
- add workspace-first flow evidence

##### Step 2: Update release notes
- record API fixes
- record new backend capabilities
- record frontend workbench boundaries

##### Step 3: Update plan status
- mark this plan as `in progress` -> `completed`

---

## 4. Execution Order

1. **Feature F1**：先关闭 2 个联调阻塞 API
2. **Feature F2 panel tasks**：按 F2-T1 -> F2-T2 -> F2-T3 -> F2-T4 -> F2-T5 -> F2-T6 -> F2-T7 -> F2-T8 顺序
3. **Feature F3**：Loop Engine state machine -> runner -> RPC
4. **Feature F4**：translator -> client -> integration
5. **Feature F5**：budget enforcement -> run log/replay
6. **Feature F6**：integration test -> full test pass -> docs

---

## 5. Verification Plan

### 5.1 Pre-Integration Blockers
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_approvals.py -v
pytest tests/test_gateway/test_rpc_loop_workspace_cost.py -v
```

### 5.2 Backend RPC
```bash
pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```

### 5.3 Loop Engine
```bash
pytest tests/test_loop_workspace/test_engine_state_machine.py tests/test_loop_workspace/test_engine_runner.py tests/test_gateway/test_rpc_loop_workspace_engine.py -v
```

### 5.4 Adapter
```bash
pytest tests/test_loop_workspace/test_mcp_client.py tests/test_loop_workspace/test_event_translator.py tests/test_loop_workspace_integration/test_cross_tool_handoff.py -v
```

### 5.5 Budget + Run Log/Replay
```bash
pytest tests/test_loop_workspace/test_budget_enforcement.py tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py tests/test_gateway/test_rpc_loop_workspace_replay.py -v
```

### 5.6 Panels
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

### 5.7 Integration
```bash
pytest tests/test_loop_workspace_integration/test_workspace_first_flow.py -v
pytest tests/test_loop_workspace tests/test_loop_workspace_integration tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py -q
```

---

## 6. Risks and Mitigations

| Risk | Mitigation |
| --- | --- | --- |
| approval/cost 修复破坏现有 schema | 只新增返回字段和 run_log cost 持久化，不删除字段 |
| Loop Engine 范围膨胀 | v0.1 只做本地最小 runner + pluggable handler |
| MCP adapter 依赖外部工具 | 先用 fake MCP server 完成 round-trip |
| 前端 panel 工作量过大 | 先做最小可用面板，再补 detail/enhancement |
| MCP stdio 测试不稳定 | 保留 process-level harness，逐步修复 legacy stdio harness |

---

## 7. Launch Criteria Mapping

| PRD Launch Criterion | Covered by |
| --- | --- |
| Workspace state can be created, inspected, exported, and resumed | Baseline done |
| LoopDesk workbench supports continuous workflow inspection and actions | Feature F2 |
| At least one MCP adapter successfully connects a local coding workflow | Feature F4 |
| Loop engine can run ad hoc loops with triage/maker/checker/escalation | Feature F3 |
| Memory supports durable storage, search, compaction, and continuity | Baseline + Feature F2 |
| Cost and approval controls are observable and enforceable | Feature F1 + Feature F5 |
| Documentation covers install, connect tools, run loops, inspect state, recover | Feature F6 |
