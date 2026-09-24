# LoopDesk v2.0 WebUI & LoopX 闭环实施方案（FDD 特性驱动设计）

> **文档版本**：v2.0.2  
> **更新时间**：2026-09-16  
> **方法论依据**：特性驱动开发（Feature-Driven Development, FDD）+ 测试驱动开发（TDD Failing-Test-First）+ Loop Engineering（Triage -> Maker -> Checker -> Escalation -> Run Log -> Stop Condition）。  
> **对齐文档**：`docs/prd/loopdesk-prd-v2.0.zh.md`、`docs/plans/loopdesk-webui-design-spec.md`（v2.0 详细设计）。

---

## 1. 整体架构与特性清单（Feature Breakdown）

依据 FDD 理念，系统交付被严格切分为具备独立业务价值的 4 个核心特性集（Feature Sets, F1 - F4），每个特性集下拆解为可独立开发、独立验证并符合 Failing-Test-First 的子任务切片。

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Feature F1: 纯前端交互契约与死控件闭环 (P0)                                            │
│ [F1.1 审批门弹窗] ➔ [F1.2 右栏折叠与快捷键] ➔ [F1.3 审批红点与筛选] ➔ [F1.4 项目切换下拉]  │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F2: Gateway REST API 与前端 Client 对接 (P0)                                  │
│ [F2.1 REST 端点契约] ➔ [F2.2 前端 API 适配层] ➔ [F2.3 状态加载与错误兜底 (C7)]          │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F3: 运行时 SSE 事件驱动与状态机实时流转 (P0)                                  │
│ [F3.1 SSE 广播事件源] ➔ [F3.2 前端事件流消费与状态同步] ➔ [F3.3 断线重连与优雅降级]       │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F4: LoopX 控制面协同与 GitHub PR 自动化交付 (P1)                                │
│ [F4.1 GitHub Issues 启用] ➔ [F4.2 LoopX 控制面初始化] ➔ [F4.3 Issue-fix 修复闭环]     │
│ ➔ [F4.4 PR 8 段自审报告生成与合流门禁判定]                                            │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 特性集详细拆解与实施规划

### Feature F1: 纯前端交互契约与死控件闭环 (Pure Frontend Interactivity)

**业务价值**：在当前 10 屏静态原型基础上，彻底打通死控件交互，形成完整的状态流转闭环，满足 PRD §9.11 的 UX 规范。

#### Task F1.1: 补齐 R4 审批门 (Gate) 决策模态窗与状态流转
- **责任范围**：`frontend/src/overlays/Modals.tsx`, `frontend/src/screens/TaskBoard.tsx`, `frontend/src/data.ts`
- **TDD 规则 / 验证标准**：
  - 测试用例：在卡片为 `blocked_on_gate`（待审批列）时，右栏展示明确的「Approve / Deny」按钮；
  - 点击「Approve」弹出审批确认弹窗，确认后卡片状态流转为已完成，离开待审批列；
  - 点击「Deny」要求录入驳回理由，确认后卡片退回进行中列。
- **Stop Condition**：通过 Playwright / 组件测试验证审批与驳回交互路径。

#### Task F1.2: 打通右栏折叠 (CloseIcon) 与全局快捷键
- **责任范围**：`frontend/src/App.tsx`, `frontend/src/screens/TaskBoard.tsx`
- **验证标准**：
  - 点击右栏顶部 `CloseIcon`，右栏平滑收起（`w-0` 或 `hidden`），中栏看板自动占满剩余宽度；
  - 在卡片被选中或点击顶部/卡片详情入口时，右栏重新展开；
  - 支持快捷键 `⌘B` 切换右栏展开/收起。

#### Task F1.3: 联动左栏 L5 审批门红点与看板快速过滤
- **责任范围**：`frontend/src/components/LeftRail.tsx`, `frontend/src/data.ts`
- **验证标准**：
  - L5 待审批项自动统计 `data.ts` 中 `gate_status === 'blocked_on_gate'` 的任务总数；
  - 点击左栏「待审批」，看板自动激活过滤，仅展示第 3 列任务。

#### Task F1.4: 激活 TopBar 与 LeftRail 的项目切换下拉菜单 (L1)
- **责任范围**：`frontend/src/components/TopBar.tsx`, `frontend/src/components/LeftRail.tsx`
- **验证标准**：
  - 点击项目选择器展开项目列表（LoopDesk 核心 / 向量检索模块 / 文档系统）；
  - 切换项目后，看板任务与团队资产数据动态按 `project_id` 过滤重载。

---

### Feature F2: Gateway REST API 与前端 Client 对接 (Backend Integration)

**业务价值**：消除前端全部纯 Mock 数据，实现前后端真实 HTTP 契约通信。

#### Task F2.1: 实现 FastAPI Gateway 任务与资产 REST 端点
- **责任范围**：`src/loopdesk/gateway/service.py`, `src/loopdesk/gateway/routes/tasks.py` (新增)
- **Failing Test First**：
  - 编写 `tests/test_gateway/test_task_routes.py`：测试获取任务列表、根据模板新建任务、获取任务详情。
  - 运行 pytest 确认预期 404/失败，随后实现 Minimal Endpoint 代码。
- **Stop Condition**：
  - `GET /api/v1/projects/{project_id}/tasks` 返回标准契约 JSON。
  - `POST /api/v1/tasks/{task_id}/gate/decision` 成功修改底层 `LOOP-STATE.json` 中的 Gate 状态。

#### Task F2.2: 前端封装 API 客户端与状态挂载
- **责任范围**：`frontend/src/api/client.ts` (新增), `frontend/src/hooks/useTasks.ts` (新增)
- **验证标准**：
  - 前端通过 Vite Proxy 代理到 `http://localhost:8000`；
  - 看板卡片与详情页数据由 `useTasks` Hook 从真实后端加载，无后端时自动优雅回退为 Mock 数据。

#### Task F2.3: 落地 C7 状态占位组件（加载骨架屏、空状态、错误重试）
- **责任范围**：`frontend/src/components/BoardStates.tsx` (新增)
- **验证标准**：
  - 接口拉取过程中展示 4 列骨架屏；
  - 任务列表为空时展示“新建第一个任务”插画与推荐模板；
  - 网络报错时展示友好错误卡片与「重试」按钮。

---

### Feature F3: 运行时 SSE 事件驱动与状态机实时流转 (Real-time Stream)

**业务价值**：Agent 运行过程中的单测输出、Token 消耗、阶段变迁与 Gate 阻断实时推送到 Web 界面，无需手动刷新。

#### Task F3.1: Gateway 实现 Server-Sent Events (SSE) 事件广播
- **责任范围**：`src/loopdesk/gateway/routes/events.py`, `src/loopdesk/engine/events.py`
- **Failing Test First**：
  - 编写 `tests/test_gateway/test_events_sse.py`，验证当 Engine 产生状态跳变时，SSE 端点能收到流式 Event 载荷。
- **Stop Condition**：SSE 端点稳定输出 `task_phase_changed`, `token_spend_updated`, `gate_blocked` 事件。

#### Task F3.2: 前端接入 SSE 并实时驱动 Stepper 与看板
- **责任范围**：`frontend/src/hooks/useTaskStream.ts`, `frontend/src/screens/TaskBoard.tsx`
- **验证标准**：
  - 接收到 `gate_blocked` 事件时，任务卡瞬间从第 2 列跳入第 3 列，右栏 R4 区域自动亮起黄色告警；
  - 实时刷新 R3 成本进度条与已耗费 Token。

#### Task F3.3: SSE 断线重连与连接状态感知
- **责任范围**：`frontend/src/components/ConnectionStatus.tsx`
- **验证标准**：网络异常断开后展示重连态势，恢复后自动重新同步最新状态。

---

---

### Feature F5: 项目管理与远端任务 MCP 前置强校验 (Project Modes & Pre-flight Guardrail)

**业务价值**：打通项目独立生命周期管理（本地 Local 目录 vs 远端 Remote 仓库），建立远端任务创建时的 MCP 前置强拦截闭环，杜绝无上下文盲目执行。

#### Task F5.1: 后端 Gateway 增加项目管理与 Pre-flight 校验 API
- **责任范围**：`src/loopdesk/gateway/tasks.py`, `src/loopdesk/gateway/projects.py` (新增)
- **Failing Test First**：
  - 编写 `tests/test_gateway/test_project_routes.py`：
    1. 测试项目创建（`POST /api/v1/projects`）：校验 `mode="local"` 绑定本地路径，`mode="remote"` 校验 Git URL 规范。
    2. 测试远端任务创建前置校验（`POST /api/v1/projects/{id}/tasks/validate`）：
       - 当项目/任务指定依赖 JIRA 且 JIRA MCP 未连接时，返回 `{"ok": false, "code": "MCP_REQUIRED", "required_connector": "jira", "message": "该远端任务依赖 JIRA MCP 连接器，当前未配置"}` 并拒绝创建；
       - 当 JIRA MCP 已就绪时，校验通过允许创建。
  - 运行 pytest 确认红灯，随后实现最小路由与校验逻辑。
- **Stop Condition**：
  - `GET /api/v1/projects` 能列出本地与远端项目；
  - 远端任务创建校验能够准确阻断未挂载 MCP 的请求并返回标准拦截码。

#### Task F5.2: 前端新建任务面板（C4）集成项目下拉与 MCP 依赖感知
- **责任范围**：`frontend/src/overlays/Modals.tsx` (`NewTaskModal`)
- **交互规范与验收标准**：
  1. 「归属项目」字段升级为真实下拉选择框（展示 Project 名称与模式徽标：`[Local]` 或 `[Remote]`），并提供「+ 新建/关联项目」快捷入口；
  2. 当用户选择远端项目或选择了外部工单模板时，界面触发状态探测；
  3. 若检测到对应 JIRA/Plane MCP 未连接，在面板下方即时渲染琥珀色警示卡片：
     > ⚠️ *当前选中的远端项目需挂载 JIRA MCP 连接器以同步工单。检测到服务未就绪。*
     并高亮展示「去配置连接器 ➔」引导按钮，同时禁用「开始任务」提交按钮；
  4. 点击引导按钮自动关闭任务弹窗并平滑切换路由至 `SettingsMcp` 界面。

### Feature F4: LoopX 控制面协同与 GitHub PR 自动化交付 (LoopX Delivery)

**业务价值**：打通外部 Issue 到自动化 PR 的全流程闭环，形成严密工程自审与合流门禁。

#### Task F4.1: 开启 GitHub 仓库 Issues 与项目环境就绪
- **执行命令**：
  ```bash
  gh repo edit JustinIan-AI/Savus --enable-issues
  gh issue list -R JustinIan-AI/Savus
  ```
- **Stop Condition**：GitHub CLI 成功返回 issue 列表，不再报错 `repository has disabled issues`。

#### Task F4.2: 初始化 LoopX 项目控制面
- **执行命令**：
  ```bash
  loopx connect --project .
  loopx status
  ```
- **Stop Condition**：`.loopx/registry.json` 生成，`loopx status` 报告状态正常。

#### Task F4.3: 基于 Issue-Fix 模板执行 TDD 红绿循环修复
- **执行流程**：
  1. 创建规范 Issue：`gh issue create --title "..." --body "..."`
  2. 启动 LoopX 受管 Goal：`loopx start-goal --project . --capability-route issue-fix`
  3. 切出隔离分支：`git checkout -b codex/issue-<id>-<slug>`
  4. Maker 阶段：编写 Failing Test，确认 `pytest` 失败红灯；
  5. 实施最小修复，确认 `pytest` 绿灯通过；
  6. Checker 阶段：固化证据 `loopx evidence-log record`。

#### Task F4.4: PR 自动封包、8 段双语 Review 与门禁合流
- **执行流程**：
  1. 提交代码并推送：`git push origin codex/issue-<id>-<slug>`；
  2. 创建 GitHub PR 并绑定 `Fixes #<id>`；
  3. 执行 LoopX 机器审查：`loopx pr-review --repo JustinIan-AI/Savus`，自动输出 8 段式中文深度审查 + 英文简要结论；
  4. 触发合流门禁校验：`loopx issue-fix pr-gate-reconcile`，核准后合入主干并关闭 Goal。

---

## 3. 回滚标准与风险处置（Rollback & Risk Plan）

1. **命名与边界违规（Escalation）**：若在 PR 或 API 中出现历史命名泄露，立即中止合并，执行命名审查。
2. **测试失败阻断**：若任何既有测试套件回归失败，禁止提交 PR，优先排查最小修复破坏面。
3. **前端 Build 失败阻断**：任何改动必须保证 `cd frontend && npm run build` 0 警告 0 报错。
