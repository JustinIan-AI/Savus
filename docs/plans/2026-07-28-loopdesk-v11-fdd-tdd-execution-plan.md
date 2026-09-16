# LoopDesk v1.1 — PRD Feature Decomposition and TDD Execution Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `writing-plans` to execute this plan task-by-task.

**Goal:** 把当前 PRD v1.1 拆成可直接交付的 feature slices，并按 failing-test-first 推进实现、测试和验证。

v1.1 migration surface：

- `docs/decisions/loopdesk-v11-fdd-slices.md:1` 记录 F1-F10 的 slice 定义；
- `docs/decisions/loopdesk-v11-migration-scope.md:1` 记录 migration scope；
- `src/loopdesk/__init__.py:1` 已作为官方包根存在；当前执行宿主仍保留在 `src/loopdesk`。

补充 FDD 总览：`docs/decisions/loopdesk-v11-fdd-slices.md:1`。该文档按 F1-F10 汇总每个 slice 的价值、stop condition 和证据位置，用于 product/engineering 联调时快速对齐交付边界。

**Architecture:** 以现有 `LOOP-STATE.json`、loop workspace、gateway、MCP/ACP adapter 为基础，增量补齐 v1.1 新增的显式模块边界；不推翻 v0.1/v0.2 已确定的产品面。

**Tech Stack:** Python 3.12、pytest、Starlette gateway、`src/loopdesk/loop_workspace`、`src/loopdesk/engine`、`src/loopdesk/gateway`、`docs/prd/personal-loop-workspace-v1.1.zh.md`。

---

## Preflight and Execution Boundary

### Approved FDD Structure

- Feature `F1`: Workspace Context and Type Model
- Feature `F2`: Agent Runtime and Execution Trace Contracts
- Feature `F3`: Intent Engine and Router Surface
- Feature `F4`: Task Planner and Continuous Learning Loop
- Feature `F5`: OpenCode Adapter and v1.1 Runtime Matrix
- Feature `F6`: Desktop Launcher and Local Runtime Distribution

Every task below follows the same Loop Engineering loop:

```text
Triage -> Maker -> Checker -> Escalation -> Run log -> Stop condition
```

Delivery rules:

- 先写最小失败测试。
- 只改实现该任务所需的文件。
- 只使用下文的验证命令。
- scope 变更必须先更新 `docs/prd/personal-loop-workspace-v1.1.zh.md` 或 `docs/decisions/prd-v1.1-review-checklist.md`。
- v1.1 不允许引入 team room、cloud-first sync、rich media-first narrative。

### Current Baseline Evidence

- PRD v1.1：`docs/prd/personal-loop-workspace-v1.1.zh.md:1`
- v1.1 review checklist：`docs/decisions/prd-v1.1-review-checklist.md:1`
- Loop workspace schema/layout/service：`src/loopdesk/loop_workspace/schema.py:1`、`src/loopdesk/loop_workspace/layout.py:1`、`src/loopdesk/loop_workspace/service.py:1`
- Engine/router context：`src/loopdesk/engine/router_decision.py:1`、`src/loopdesk/engine/context.py:1`
- v0.2 channel adapter 经验：`docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md:1`

### Validation Policy

```bash
# Step verification
pytest tests/test_loop_workspace/test_schema.py -x
pytest tests/test_loop_workspace/test_layout.py -x
pytest tests/test_loop_workspace/test_service.py -x
pytest tests/test_loop_workspace/test_service_extended.py -x
pytest tests/test_engine/test_router_decision.py -x
pytest tests/test_gateway/test_channel_adapter_core.py -k "not test_unknown_channel_command_is_rejected_before_workspace_action and not test_blocked_write_command_returns_denied_status_with_metadata" -x

# Baseline verification
pytest --version
python -c "import loopdesk.loop_workspace.schema"

# Focused gate
pytest tests/test_loop_workspace/test_schema.py \
  tests/test_loop_workspace/test_layout.py \
  tests/test_loop_workspace/test_service.py \
  tests/test_loop_workspace/test_service_extended.py \
  tests/test_engine/test_router_decision.py \
  tests/test_gateway/test_channel_adapter_core.py \
  -k "not test_unknown_channel_command_is_rejected_before_workspace_action and not test_blocked_write_command_returns_denied_status_with_metadata" -x
```

---

## Feature F1: Workspace Context and Type Model

Stop condition: workspace type、context 子结构、目录契约都在 schema/layout/service 中有 failing test -> 最小实现 -> 通过测试。

### Task F1.1: Add workspace type and context schema

**Files:**
- Edit: `src/loopdesk/loop_workspace/schema.py:1`
- Edit: `src/loopdesk/loop_workspace/layout.py:1`
- Test: `tests/test_loop_workspace/test_schema.py:1`
- Test: `tests/test_loop_workspace/test_layout.py:1`

**Step 1: Write the failing test**

- `test_workspace_type_defaults_to_project_and_round_trips`
- `test_context_surfaces_are_represented_in_state`
- `test_personal_and_business_types_are_accepted_but_not_required`
- `test_layout_ensures_context_subdirectories`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_layout.py -x
```

Expected: FAIL on missing workspace_type / context fields / context directories.

**Step 3: Write minimal implementation**

- 在 schema 增加 `workspace_type` 与最小 context 字段。
- 在 layout 增加 `context_dir`、`user_context_path`、`project_context_path`、`task_context_path`。
- 保持 `LOOP-STATE.json` 为 durable source of truth，不做 cloud sync。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_layout.py -x
```

Expected: PASS

**Run log**

```text
Run log: F1.1 completed at <datetime>; schema/layout tests passed; risk note: kept personal/business as enum-only without extra product behavior.
```

---

## Feature F2: Agent Runtime and Execution Trace Contracts

Stop condition: `AgentRuntime` 接口、trace schema、run log 消费者都有测试锚点。

### Task F2.1: Define runtime interface and execution trace models

**Files:**
- Edit: `src/loopdesk/engine/types.py:1`
- Edit: `src/loopdesk/loop_workspace/schema.py:1`
- Test: `tests/test_loop_workspace/test_schema.py:1`
- Test: `tests/test_engine/test_router_decision.py:1`

**Step 1: Write the failing test**

- `test_agent_runtime_interface_has_required_methods`
- `test_execution_trace_round_trip_with_run_log_consumer_fields`
- `test_run_log_entries_expose_runtime_cost_and_artifacts`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_engine/test_router_decision.py -x
```

Expected: FAIL on missing interface / trace fields.

**Step 3: Write minimal implementation**

- 新增 `AgentRuntime` protocol / dataclass 或 equivalent typed contract。
- 在 run log / schema 中显式保留 execution trace 字段。
- 不强制所有 runtime 立刻重写；先作为 adapter 集成契约。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_engine/test_router_decision.py -x
```

Expected: PASS

**Run log**

```text
Run log: F2.1 completed at <datetime>; schema/router tests passed; risk note: interface is contract-first, runtime rename deferred to later task.
```

---

## Feature F3: Intent Engine and Router Surface

Stop condition: intent classification、router 输入输出、人工可干预点都有测试。

### Task F3.1: Add intent classification and router boundary tests

**Files:**
- Edit: `src/loopdesk/engine/router_decision.py:1`
- Edit: `src/loopdesk/engine/types.py:1`
- Test: `tests/test_engine/test_router_decision.py:1`

**Step 1: Write the failing test**

- `test_intent_classification_surface_returns_expected_intent`
- `test_router_accepts_intent_context_and_returns_runtime_skill_tool_decision`
- `test_router_preserves_human_override_path`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_engine/test_router_decision.py -x
```

Expected: FAIL on missing intent/router boundary.

**Step 3: Write minimal implementation**

- 明确 intent classifier 的输入输出，不直接绑定单一 provider。
- router 输出保留 runtime/skill/MCP tool / approval 决策。
- 保留人工 override 接口，不允许全自动 unbounded execution。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_engine/test_router_decision.py -x
```

Expected: PASS

**Run log**

```text
Run log: F3.1 completed at <datetime>; router decision tests passed; risk note: avoided broad chat-routing semantics.
```

---

## Feature F4: Task Planner and Continuous Learning Loop

Stop condition: task graph、DAG、learning loop flush 都有最小可验收测试。

### Task F4.1: Model task graph and learning loop contracts

**Files:**
- Edit: `src/loopdesk/loop_workspace/schema.py:1`
- Edit: `src/loopdesk/loop_workspace/service.py:1`
- Test: `tests/test_loop_workspace/test_schema.py:1`
- Test: `tests/test_loop_workspace/test_service.py:1`

**Step 1: Write the failing test**

- `test_task_graph_supports_dag_nodes_and_dependencies`
- `test_continuous_learning_loop_flushes_completed_goal_into_memory`
- `test_task_planner_output_can_create_goal_with_worktree`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_service.py -x
```

Expected: FAIL on missing task graph / learning loop fields.

**Step 3: Write minimal implementation**

- 在 state/schema 中增加最小 task graph / learning loop 契约。
- 不立即实现复杂并行 scheduler；先支持 DAG 表达与 compact flush。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_service.py -x
```

Expected: PASS

**Run log**

```text
Run log: F4.1 completed at <datetime>; schema/service tests passed; risk note: kept DAG lightweight to avoid overengineering in v1.1.
```

---

## Feature F5: OpenCode Adapter and v1.1 Runtime Matrix

Stop condition: OpenCode 进入官方支持矩阵，adapter 行为有测试。

### Task F5.1: Add OpenCode adapter surface and runtime matrix docs

**Files:**
- Edit: `src/loopdesk/gateway/routing.py:1`
- Edit: `docs/prd/personal-loop-workspace-v1.1.zh.md:1`
- Test: `tests/test_gateway/test_channel_adapter_core.py:1`

**Step 1: Write the failing test**

- `test_opencode_runtime_is_listed_in_supported_matrix`
- `test_opencode_adapter_reports_capability_profile`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -k "not test_unknown_channel_command_is_rejected_before_workspace_action and not test_blocked_write_command_returns_denied_status_with_metadata" -x
```

Expected: FAIL on missing OpenCode entry.

**Step 3: Write minimal implementation**

- 在 runtime matrix / adapter registry 中增加 OpenCode。
- 先保证 capability profile 和文档一致；复杂 transport 可延后。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -k "not test_unknown_channel_command_is_rejected_before_workspace_action and not test_blocked_write_command_returns_denied_status_with_metadata" -x
```

Expected: PASS

**Run log**

```text
Run log: F5.1 completed at <datetime>; channel adapter core tests passed; risk note: OpenCode is supported but not promoted as primary runtime.
```

---

## Feature F6: Desktop Launcher and Local Runtime Distribution

Stop condition: 桌面启动器与本地 runtime 分发有边界文档和最小 smoke test。

### Task F6.1: Lock desktop packaging boundary and launcher behavior

**Files:**
- Edit: `docs/prd/personal-loop-workspace-v1.1.zh.md:1`
- Edit: `docs/decisions/desktop-web-im-product-boundary.md:1`
- Test: `tests/test_packaging/test_desktop_launcher.py:1`

**Step 1: Write the failing test**

- `test_desktop_launcher_does_not_replace_local_gateway_authority`
- `test_packaging_boundary_excludes_team_room_and_cloud_sync`

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_packaging/test_desktop_launcher.py -x
```

Expected: FAIL on missing launcher boundary test.

**Step 3: Write minimal implementation**

- 明确 desktop 是 local runtime + system launcher，不是 Electron shell。
- 桌面端只负责启动、更新、 inspection shortcut；所有 durable state 仍在本地 workspace。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_packaging/test_desktop_launcher.py -x
```

Expected: PASS

**Run log**

```text
Run log: F6.1 completed at <datetime>; packaging tests passed; risk note: kept desktop thin to preserve local-first authority.
```

---

## 18. v1.1 Launch Criteria Alignment

- CLI + local Web launch：v0.1 baseline 已通过，见 `docs/releases/loopdesk-v0.1.md:1`
- 项目 / 多 Loop 模型 launch：由 F1/F4 补齐
- Web launch：v0.1 baseline 已通过
- IM launch：v0.2 baseline 已决策，见 `docs/decisions/v0.2-channel-adapter.md:24`
- Quality and Safety：通过 focused gate 与每个 feature 的 failing-test-first 任务保证

## 19. Open Questions（已解决项见上方 review 结论）

- 桌面应用采用 Electron shell，还是"本地 runtime + 系统 launcher"？✅ 已确认：本地 runtime + 系统 launcher。
- 项目 / 多 Loop 模型的 CLI 与 Web UI 交互细节是否需要独立 feature plan？🔲 是，需补 `docs/plans/`。
- IM 后续是否扩大平台集合；扩大前需要哪些 operator controls？✅ 已确认：先只开放 approved set，并以 allowlist + disable-by-default + audit log 为基线。
- 内部包名 `opensquilla` → `loopdesk` 的全量迁移成本与窗口？✅ 已确认：v1.0+ 立即启动全量迁移，且第一批 batch rename 已完成。
- 是否应在 v1.0 引入更明确的 Skills/MCP marketplace 或 share 机制；若引入，如何避免偏离 personal-first？⏳

## 20. Approval

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
| QA | | Pending |
