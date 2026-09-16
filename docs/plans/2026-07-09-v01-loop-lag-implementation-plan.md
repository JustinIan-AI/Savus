# LoopDesk v0.1 / 前后端联调 Lag 实施计划

> Date: 2026-07-09
> Status: ready for review
> Owner: Product / Engineering / QA
> Prerequisite: `docs/plans/2026-07-09-v01-gap-implementation-plan.md` Phase 1 Backend RPC Completion 的骨架结果已落地，但联调前仍有两个阻塞测试未关闭
> Goal: 把 v0.1 剩余主要 gap 收敛为可执行、可验收的实施计划，并明确联调前 API 缺口

---

## 0. 当前基线

### 已验证现状
- `loop_workspace` 已注册 `29` 个 RPC，覆盖 workspace、memory、skills、approvals、cost、run log、worktree、templates 等后端能力。
- 定向 backend RPC 测试：13 passed / 2 failed / 1 collection error。
  - 通过：`tests/test_gateway/test_rpc_loop_workspace.py`、`tests/test_gateway/test_rpc_loop_workspace_memory.py`、`tests/test_gateway/test_rpc_loop_workspace_skills.py`、`tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_set_budget`、`tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_run_log_list`、`tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approvals_list`、`tests/test_gateway/test_rpc_loop_workspace_extended.py`
  - 失败：`tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond`、`tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history`
  - 收集报错：`tests/test_gateway/test_loop_workspace_view_static.py`（`ImportError: cannot import name 'LOOP_WORKSPACE_VIEW_FILES' from 'loopdesk.gateway.control_ui'`）
- Web UI LoopDesk 工作台已有独立 `loop_workspace.js/css`，但目前仍以静态观察为主：
  - `src/loopdesk/gateway/static/js/views/loop_workspace.js` 仅调用 `loop_workspace.get`、`loop_workspace.export`、`loop_workspace.resume`
  - 尚未实现 header 编辑、memory/skills/approvals/worktree/run log/cost history 等交互面板
- PRD / 核心功能 / 验收文档仍把 Loop Engine、Cross-Tool Adapter、真实 budget enforcement、session resume/replay/compaction、完整交互工作台列为 v0.1 交付范围；当前代码均未实现。
- 前端 Approvals/Skills 视图仍使用 legacy `exec.proposals.*` / `/api/approvals`，未接入 `loop_workspace.approvals.list` / `loop_workspace.approval.respond` 的 workspace-first 模型。

### 一句话结论
- 联调前不是“没有 API”，而是“后端骨架 API 已有，但还有 2 个阻塞 bug 没关，且 v0.1 还有 4 大块产品能力 / 5 组新增/修正 API 未交付”。
- 若把“已落地但阻塞联调”也算成缺失，则联调前有 `2` 个 API 端口行为不符预期；若按 PRD/功能完整度算，v0.1 还有 `5` 个主要交付块未完成。

---

## 1. 交付边界与口径

### 1.1 LoopDesk v0.1 不包含项
- 多渠道协作、team room、cloud-first sync、marketplace skills、heavy desktop GUI
- ACP 为第二路径，v0.1 以 MCP-first 本地工作流为主
- legacy `session` / `workspace-state.json` / channel-first 叙事不得作为 v0.1 公开表面

### 1.2 本计划覆盖项
- 关闭 LoopDesk 工作台联调前的 backend API bug / collection gap
- 补齐 workspace-first 的前端交互面板
- 补齐 PRD 未覆盖的 Loop Engine、Adapters、Budget Enforcement、Run Log / Replay、Docs/Tests/Release gates
- 所有实现必须先用 failing test 覆盖，再进入最小实现

---

## 2. 联调前 API 缺口

### 2.1 已注册但联调前行为不符合预期的 API（2 个）
| 序号 | API | 当前状态 | 阻塞原因 | 验收要求 |
| --- | --- | --- | --- | --- |
| API-1 | `loop_workspace.approval.respond` | 已注册，但返回 `None` | 当前实现只写 approval 记录，未返回 `current_state()` | 前端 Approvals / 工作台可基于返回 payload 直接刷新 approvals + safety/cost |
| API-2 | `loop_workspace.cost.history` | 已注册，但历史为 `0` | 当前只扫描 `run_log` 里的 `cost` 字段，而 `record_run_log` 未把 `cost_payload` 持久化到 run_log entry | 前端 Cost/Safety panel 可展示至少 1 条历史 cost event |

### 2.2 PRD 与联调相关的支持 API 缺口（5 组）
| 序号 | API 组 | 缺失原因 | 影响 |
| --- | --- | --- | --- |
| API-3 | Loop Engine：`engine.start/stop/status/step/set_stop_condition` | PRD 要求 LoopDesk 核心能力，代码为 `0` | 前端无法展示 triage/maker/checker/escalation 连续工作流 |
| API-4 | Cross-Tool Adapter：真实 MCP 握手 / tool event -> workspace state | 当前只有本地 stdio server / context pack 骨架 | 至少一个本地 coding workflow 无法形成真正闭环 |
| API-5 | Budget Enforcement：`cost.enforce` 或等价运行时拦截 | 当前只有 budget cap schema + history | denylist / kill switch / budget exceeded 无法自动切 report-only 或暂停 |
| API-6 | Resume / Replay / Compaction 工作流 API | 当前只有 memory append/search/compact/resume_pack，无 session resume/replay | 前端无法提供失败恢复、复盘、上下文续接能力 |
| API-7 | LoopDesk 工作台前端交互 API 接线 | 当前仅 `get/export/resume`，缺少 `update/templates.apply/memory/skills/approvals/worktree/run_log/cost` 交互调用 | 前端无法达到 PRD 的“统一连续工作流工作台” |

### 2.3 结论
- 严格按“联调前还缺多少个 API 端口”回答：`2` 个阻塞 bug。
- 按“v0.1 交付还有多少主要 API/能力 gap”回答：`5` 组主要缺口 + `2` 个阻塞 bug。
- 建议在正式联调前，先修复 API-1/API-2，否则前端必须额外写 fallback 或 mock，联调可信度会下降。

---

## 3. v0.1 主要 Gap 总览

### 3.1 已实现（可作为复用的 runtime）
- `LOOP-STATE.json` schema / serialization / layout / repository
- CLI：`init/show/update/resume/export/worktree/cost/kill-switch/denylist`
- MCP stdio：`get_context_pack/list_templates/read_template/run_local_command`
- 后端 RPC 骨架：workspace / memory / skills / approvals / cost / run log / worktree / templates
- Web UI 静态工作台外壳 + legacy approvals/skills views

### 3.2 尚未实现（v0.1 交付缺口）
| 序号 | Gap | PRD 依据 | 对联调的影响 |
| --- | --- | --- | --- |
| G1 | Loop Engine（triage/maker/checker/escalation/stop condition） | 核心不同点 | 前端只能展示状态，不能展示真正的工作流推进 |
| G2 | Cross-Tool Adapter（至少一个真实 coding workflow） | F3 | 前端无法验证跨工具连续工作流 |
| G3 | Budget Enforcement runtime（自动暂停/拒绝/escalation） | F5 | 前端 safety/cost 只能展示，不能驱动后端行为 |
| G4 | Run Log / Replay / Compaction 用户工作流 | F4/F6 | 前端缺少复盘与失败恢复入口 |
| G5 | 前端交互面板与 workspace-first 信息架构 | PRD §7 | 当前页面更像 legacy dashboard，不是 LoopDesk 工作台 |

---

## 4. 实施计划

> 所有任务必须遵循：先写 failing test → 运行失败 → 最小实现 → 运行定向测试 → 再推进。

### Phase 0：联调前置修复（Blocking）

#### Task 0.1：修复 approval.respond 返回值
**Files:**
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_approvals.py`

**Step 1：定位问题**
- `tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond` 当前报 `TypeError: 'NoneType' object is not subscriptable`
- 根因：`loop_workspace.approval.respond` 调用 `service.record_approval(...)` 后没有返回 `service.current_state()`

**Step 2：修复实现**
- 让 `loop_workspace.approval.respond` 返回 approval 列表和当前 `current_state()`
- 保证前端可直接使用返回 payload 刷新 Approvals 与 Safety/Cost 区块

**Step 3：验证**
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_approvals.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```

#### Task 0.2：修复 cost.history 与 run_log cost 持久化
**Files:**
- Edit: `src/loopdesk/loop_workspace/service.py`
- Edit: `src/loopdesk/loop_workspace/schema.py` 或 `src/loopdesk/loop_workspace/repository.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_cost.py`

**Step 1：定位问题**
- `tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history` 期望 `total == 1`，实际为 `0`
- 根因：`record_run_log` 只调用 `state.record_cost(run_log["cost"])`，但该 cost 未进入 `run_log` entry；`cost.history` 只扫描 run_log

**Step 2：修复实现**
- `record_run_log` 接收到的 cost 要同步写回 run_log entry
- 保持现有 `state.record_cost(...)` 不变，只补充 run_log entry 的 cost 字段
- `cost.history` 继续从 run_log 聚合，或改为从 `cost_observatory` 返回结构化事件

**Step 3：验证**
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_cost.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_extended.py -q
```

#### Task 0.3：修复 LoopDesk 工作台静态视图 collection 问题
**Files:**
- Edit: `src/loopdesk/gateway/control_ui.py`
- Edit: `tests/test_gateway/test_loop_workspace_view_static.py`

**Step 1：定位问题**
- 收集阶段报 `ImportError: cannot import name 'LOOP_WORKSPACE_VIEW_FILES'`
- 根因：测试期望的控制 UI 常量/注册方式与当前 `control_ui.py` 不一致

**Step 2：修复实现**
- 最小修复：暴露 `LOOP_WORKSPACE_VIEW_FILES` 或更新测试为当前 control UI 的稳定接口
- 目标：让静态视图测试通过，避免联调前“连页面入口都跑不通”

**Step 3：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_view_static.py -v
```

### Phase 1：v0.1 Backend Completion

#### Task 1.1：Loop Engine 核心
**Files:**
- Create: `src/loopdesk/loop_workspace/engine/state_machine.py`
- Create: `src/loopdesk/loop_workspace/engine/runner.py`
- Test: `tests/test_loop_workspace/test_engine_state_machine.py`
- Test: `tests/test_loop_workspace/test_engine_runner.py`

**Implementation:**
- 新增 `LoopPhase = discovery | triage | maker | checker | escalation | completed | failed | paused`
- 新增 `LoopEngineState`：phase、goal、stop_condition、max_iterations、current_iteration、triage_result、maker_result、checker_result、escalation_reason
- 状态机：
  - `planned` → `triage`
  - `triage` → `maker` 或 escalation/paused
  - `maker` → `checker`
  - `checker` → `completed` / `maker` / `escalation` / `paused`
  - 任意态可因 kill switch / budget exceeded / repeated failure / ambiguous 进入 `escalation` 或 `paused`
- Runner 每一步：
  - 读取 workspace 的 budget/kill switch/denylist
  - 写结构化 `run_log`
  - 支持 stop condition / max iterations / abort

**Step 1：Failing test**
- 写 triage→maker 转换失败测试：ambiguous input 应 escalation，不允许直接进入 maker

**Step 2：实现**
- 最小实现：state machine + runner 骨架 + 默认 handler（noop/echo，便于联调）

**Step 3：验证**
```bash
pytest tests/test_loop_workspace/test_engine_state_machine.py tests/test_loop_workspace/test_engine_runner.py -v
```

#### Task 1.2：Loop Engine RPC
**Files:**
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_engine.py`

**New endpoints (5):**

| Endpoint | Method | Params |
| --- | --- | --- |
| `loop_workspace.engine.start` | write | `root`, `goal?`, `stop_condition?`, `max_iterations?` |
| `loop_workspace.engine.stop` | write | `root` |
| `loop_workspace.engine.status` | read | `root` |
| `loop_workspace.engine.step` | write | `root` |
| `loop_workspace.engine.set_stop_condition` | write | `root`, `stop_condition` |

**Step 1：Failing test**
- `engine.start` 必须创建 engine state 并写第一条 run_log

**Step 2：实现**
- 委托给 `LoopEngineRunner.run(...)` / `.step(...)`
- `engine.stop` 写入 stop reason 并把 phase 设为 paused/completed

**Step 3：验证**
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_engine.py -v
pytest tests/test_gateway/test_rpc_loop_workspace.py -q
```

#### Task 1.3：Budget Enforcement Runtime
**Files:**
- Edit: `src/loopdesk/loop_workspace/service.py`
- Edit: `src/loopdesk/loop_workspace/schema.py`
- Edit: `src/loopdesk/loop_workspace/engine/runner.py`
- Test: `tests/test_loop_workspace/test_budget_enforcement.py`

**Implementation:**
- 新增 `loop_workspace.cost.enforce` 语义：在每次 engine step / tool event / record_cost 前检查 budget cap、denylist、repeated failure
- 超过阈值时：
  - `budget exceeded` → `paused` + escalation reason
  - `denylist hit` → `paused` + approval queue
  - `repeated failure` → `escalation`
- `cost_observatory` 增加 `status: ok | warning | paused | exceeded`

**Step 1：Failing test**
- 一个超过 budget cap 的场景必须自动变为 paused

**Step 2：实现**
- 最小 enforcement：service 层方法 + engine runner 前置检查

**Step 3：验证**
```bash
pytest tests/test_loop_workspace/test_budget_enforcement.py -v
```

#### Task 1.4：Cross-Tool Adapter（至少一个真实 coding workflow）
**Files:**
- Create: `src/loopdesk/loop_workspace/adapters/mcp_client.py`
- Edit: `src/loopdesk/loop_workspace/mcp.py`
- Test: `tests/test_loop_workspace/test_mcp_client.py`
- Test: `tests/test_loop_workspace_integration/test_cross_tool_handoff.py`

**Implementation:**
- 最小 real MCP client：`connect/initialize/list_tools/call_tool`
- tool event -> workspace state：
  - stdout/stderr/artifacts 写 artifacts
  - 结果写 `run_log`
  - approvals/cost 写回 state
- v0.1 只要求至少一个本地 coding workflow 跑通 round-trip

**Step 1：Failing test**
- 从 workspace 初始化 context pack → tool 接收 → tool 结果回填 → 验证 run_log + artifacts

**Step 2：实现**
- 先支持本地 stdio，不要求网络 vendor

**Step 3：验证**
```bash
pytest tests/test_loop_workspace/test_mcp_client.py tests/test_loop_workspace_integration/test_cross_tool_handoff.py -v
```

#### Task 1.5：Run Log / Replay / Compaction 工作流 API
**Files:**
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py`
- Edit: `src/loopdesk/loop_workspace/service.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_replay.py`
- Test: `tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py`

**New endpoints (3):**

| Endpoint | Method | Params |
| --- | --- | --- |
| `loop_workspace.run_log.detail` | read | `root`, `workId?` |
| `loop_workspace.replay.pack` | read | `root`, `workId?` |
| `loop_workspace.session.compact` | write | `root`, `keep_recent?` |

**Implementation:**
- `run_log.detail` 返回单条 run_log + 关联 approval/cost/memory
- `replay.pack` 构造恢复上下文：run_log + memory + skills + template
- `session.compact` 复用 memory compaction + run_log truncation

**Step 1：Failing test**
- 5 条 run log → compact 为 2 条 + replay pack 仍能恢复上下文

**Step 2：验证**
```bash
pytest tests/test_gateway/test_rpc_loop_workspace_run_log_detail.py tests/test_gateway/test_rpc_loop_workspace_replay.py -v
```

### Phase 2：Web UI Interactive Panels

#### Task 2.1：LoopDesk 工作台主信息区
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Edit: `src/loopdesk/gateway/static/css/views/loop_workspace.css`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.list` → workspace selector dropdown
- `loop_workspace.update` → inline intent / status / template 编辑
- `loop_workspace.templates.apply` → template quick switch
- `loop_workspace.resume` → resume work

**Step 1：Failing test**
- 用户选择 workspace、切换 template、更新 intent 后，界面必须反映最新 state

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.2：Cost + Safety Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.cost.history` → cost event list
- `loop_workspace.cost.set_budget` → budget cap 输入
- `loop_workspace.cost.enforce` → 自动暂停提示（若已实现）
- `loop_workspace.set_kill_switch` → emergency pause toggle
- `loop_workspace.set_denylist` → denylist editor
- `loop_workspace.record_cost` → 被动展示

**Step 1：Failing test**
- set budget -> history 出现事件 -> kill switch 触发后 status 更新

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.3：Approval Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.approvals.list` → 待审批列表
- `loop_workspace.approval.respond` → approve/deny
- 保留 legacy Approvals view，但工作台内提供 continuous workflow 视角

**Step 1：Failing test**
- workspace 内审批 approve/deny 后立即刷新，不切到 legacy view

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.4：Memory Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.memory.search` → 搜索框
- `loop_workspace.memory.append` → 新增 memory
- `loop_workspace.memory.compact` → compact
- `loop_workspace.memory.resume_pack` → 导出/预览 resume pack

**Step 1：Failing test**
- append -> search -> compact -> resume_pack 完整链路通过

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.5：Skills Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.skills.list` → skills 列表
- `loop_workspace.skills.inspect` → 详情
- `loop_workspace.skills.audit` → audit 徽章

**Step 1：Failing test**
- skill inspect 在 workspace 侧显示，不依赖 legacy skills marketplace UI

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.6：Worktree Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.worktree.list` → worktree 列表
- `loop_workspace.worktree.create` → create dialog
- `loop_workspace.worktree.remove` → remove with retain

**Step 1：Failing test**
- create -> list -> remove 在 panel 内完成

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.7：Run Log Detail Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.run_log.list` → 分页 run log
- `loop_workspace.run_log.detail` → 展开 entry

**Step 1：Failing test**
- 10 条 run log -> 分页 -> detail 展示 cost/approval 关联

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

#### Task 2.8：Loop Engine Panel
**Files:**
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_loop_workspace_panels.py`

**Wire endpoints:**
- `loop_workspace.engine.status` → phase badge
- `loop_workspace.engine.start` → start loop
- `loop_workspace.engine.stop` → stop loop
- `loop_workspace.engine.step` → single step
- `loop_workspace.engine.set_stop_condition` → stop condition 编辑

**Step 1：Failing test**
- 启动 loop -> step -> stop -> status 更新 -> run log 可见

**Step 2：验证**
```bash
pytest tests/test_gateway/test_loop_workspace_panels.py -v
```

### Phase 3：Integration & Release Gates

#### Task 3.1：定向集成测试
**Files:**
- Create: `tests/test_loop_workspace_integration/test_workspace_first_flow.py`
- Edit: `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`

**Implementation:**
- 一个完整场景：
  1. `init` workspace + select template
  2. `engine.start`
  3. `approval.respond` / `memory.append`
  4. `run_log.list` + `cost.history`
  5. 前端 panel 刷新
  6. `worktree.create` + `engine.stop`

**Step 1：Failing test**
- 使用 TestClient / 脚本模拟前端 RPC 序列，断言 state 最终一致

**Step 2：验证**
```bash
pytest tests/test_loop_workspace_integration/test_workspace_first_flow.py -v
```

#### Task 3.2：全量定向测试
**Files:**
- All touched tests

**Verification:**
```bash
pytest tests/test_loop_workspace tests/test_loop_workspace_integration tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_approvals.py tests/test_gateway/test_rpc_loop_workspace_cost.py tests/test_gateway/test_rpc_loop_workspace_extended.py tests/test_gateway/test_rpc_loop_workspace_memory.py tests/test_gateway/test_rpc_loop_workspace_skills.py -q
```

#### Task 3.3：文档与 release notes 更新
**Files:**
- Edit: `docs/plans/loopdesk-webui-design-spec.md`
- Edit: `docs/prd/personal-loop-workspace.md`
- Edit: `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
- Edit: `docs/releases/loopdesk-v0.1.md`

**Implementation:**
- 更新 API contract 表
- 更新前端工作台接线说明
- 更新 v0.1 acceptance checklist 与 release notes
- 若有 legacy approval/skills view 仍保留，必须在 docs 中注明“v0.1 主表面为 LoopDesk 工作台”

---

## 5. 联调前检查清单

在开始前后端联调前，以下必须全部通过：

- [ ] `tests/test_gateway/test_rpc_loop_workspace_approvals.py::test_rpc_loop_workspace_approval_respond` PASSED
- [ ] `tests/test_gateway/test_rpc_loop_workspace_cost.py::test_rpc_loop_workspace_cost_history` PASSED
- [ ] `tests/test_gateway/test_loop_workspace_view_static.py` collection + PASSED
- [ ] Loop Engine 至少 5 个 RPC 注册并通过定向测试
- [ ] Budget enforcement runtime 至少 1 个测试通过
- [ ] Cross-tool handoff integration test 至少 1 个通过
- [ ] LoopDesk 工作台主视图具备：header/edit、cost/safety、approval、memory、skills、worktree、run log、engine panel 八个交互区域的最小可用版本
- [ ] 定向集成测试 `test_workspace_first_flow.py` PASSED
- [ ] v0.1 acceptance checklist / release notes 已同步

---

## 6. 验收标准

- 所有 loop workspace 定向测试通过
- 联调前 API 阻塞数为 `0`
- 前端工作台至少调用以下后端能力：
  - workspace 管理：`get/list/update/resume/export`
  - memory：`append/search/compact/resume_pack`
  - skills：`list/inspect/audit`
  - approvals：`list/respond`
  - cost/safety：`set_budget/history/set_kill_switch/set_denylist`
  - run log：`list/detail/record_run_log`
  - worktree：`create/list/remove`
  - loop engine：`start/stop/status/step/set_stop_condition`
- 至少一个本地 coding workflow 通过 MCP adapter 跑通 round-trip
- budget exceeded / kill switch / denylist / ambiguous escalation 至少各有一个定向测试
- docs 覆盖 install、connect tools、run loops、inspect state、approval、cost、failure recovery

---

## 7. 执行顺序建议

1. Phase 0 Task 0.1 -> approval.respond
2. Phase 0 Task 0.2 -> cost.history + run_log cost 持久化
3. Phase 0 Task 0.3 -> static view collection
4. Phase 1 Task 1.1/1.2 -> Loop Engine
5. Phase 1 Task 1.4 -> Cross-Tool Adapter
6. Phase 1 Task 1.3/1.5 -> Budget Enforcement + Run Log/Replay
7. Phase 2 Task 2.1-2.8 -> 前端交互面板
8. Phase 3 -> 集成测试、文档、release notes

---

## 8. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| approval/cost 修复影响现有 schema | 只扩展返回值和 run_log cost 字段，不删字段 |
| Loop Engine 范围膨胀 | v0.1 只做本地最小 runner，不接云任务 |
| Adapter 测试依赖外部工具 | 先用 fake MCP server 完成 round-trip |
| 前端 panel 工作量过大 | 先做最小交互，再补 detail panel |
| 测试环境 MCP stdio 不稳定 | 继续保留 process-level 测试 + 逐步修复 legacy stdio harness |

---

## 9. 关联文档

- `docs/plans/2026-07-09-v01-gap-implementation-plan.md`
- `docs/plans/2026-07-07-loopdesk-implementation-plan.md`
- `docs/prd/personal-loop-workspace.md`
- `docs/features/loopdesk-v0.1-feature-breakdown.md`
- `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
