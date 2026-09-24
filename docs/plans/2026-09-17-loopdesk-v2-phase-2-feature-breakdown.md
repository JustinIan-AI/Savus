# LoopDesk v2.0 第二阶段特性拆解方案（FDD 特性驱动设计）

> **文档版本**：v2.0.0  
> **更新时间**：2026-09-17  
> **方法论依据**：特性驱动开发（Feature-Driven Development, FDD）+ 测试驱动开发（TDD Failing-Test-First）+ 循环工程（Loop Engineering: Triage -> Maker -> Checker -> Escalation -> Run Log -> Stop Condition）。  
> **对齐文档**：
> 1. 产品定位权威：`docs/product-positioning.md`（v2.0 团队循环工作区）
> 2. 权威 PRD：`docs/prd/loopdesk-prd-v2.0.zh.md`（§9 需求清单）
> 3. 第一阶段实施方案：`docs/plans/2026-09-14-loopdesk-v2-gap-analysis-and-implementation-plan.md`（Feature F1 - F5）
> 4. 端到端流程标准：`docs/plans/2026-09-16-issue-fix-end-to-end-flow.zh.md`
> 5. 设计系统规范：`docs/design-system.md`（v2.0 Emerald Token）

---

## 1. 阶段目标与全景范围（Phase 2 Scope & Overview）

在第一阶段（Feature F1 ~ F5）中，LoopDesk 完成了 **Codex 三栏前端信息架构搭建、任务生命周期状态机与审批门 REST/SSE 连通、多项目切换隔离以及远程任务 MCP 前置强校验**。

第二阶段的目标是将 PRD §9.1 ~ §9.9 中剩余的 **106 项核心能力全面拆解为可执行的工程特性（Feature F6 ~ F10）**，从「单机任务看板与前端交互」深入至 **「团队长任务模板引擎、Git 原生资产分发、Local-first 多 Agent 编排、外部系统双向集成、以及企业级治理与三层记忆」**。

### 1.1 特性全景映射表（F6 ~ F10）

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Feature F6: 长任务模板引擎与标准化交付流 (P0)                                           │
│ 对齐: LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08, LOOP-11, LOOP-12, LOOP-14,         │
│       LOOP-15, LOOP-16, LOOP-17, LOOP-18, LOOP-19, LOOP-20, LOOP-21, SURF-09, SURF-10 │
│ 核心: issue-fix / pr-commit / auto-research 模板、Handoff Packet、Goal 时间线          │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F7: Git 原生团队 AI 资产市场与一键下发 (P0)                                     │
│ 对齐: ASSET-01 ~ ASSET-14, SURF-13                                                    │
│ 核心: Rules/Specs/Skills/MCP 注册中心、Git 共享、Distributor 一键下发、版本锁定与回滚 │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F8: Local-first Agent 注册表与多 Runtime 编排调度 (P0)                          │
│ 对齐: ORCH-01 ~ ORCH-13, SURF-03, SURF-04                                             │
│ 核心: claude/codex/pi 本地调度、Task Router 路由、Worktree 隔离扇出、真实 PTY 托管    │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F9: 外部系统双向集成与 MCP 连接器生态 (P0)                                      │
│ 对齐: SYS-02 ~ SYS-11                                                                 │
│ 核心: JIRA/Plane 双向同步、Confluence 知识索引、MCP 热插拔与工具调用审计溯源          │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ Feature F10: 团队级治理、多级审批门禁、安全护栏与记忆提炼 (P0)                           │
│ 对齐: GOV-01 ~ GOV-16, WS-05 ~ WS-09, CTX-01 ~ CTX-13, LOOP-09, LOOP-10, LOOP-13,     │
│       LEARN-01 ~ LEARN-08, SURF-05, SURF-07, SURF-08, SURF-11                          │
│ 核心: 五级 Gate 门禁体系、五层安全语法、三层记忆与 Memory Dream、成本硬护栏与持续学习   │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 特性集详细拆解（Detailed Feature Breakdown）

### Feature F6: 长任务模板引擎与标准化交付流 (Long-running Task Template Engine & Delivery Flows)

**业务价值**：将 LoopX 经验沉淀为内置标准模板，让开发者能够一键发起 issue-fix、pr-commit 与 auto-research 长任务，具备状态断点保存、Handoff 交接及时间旅行回退能力。

#### 需求覆盖清单
- `LOOP-04`: 长任务模板引擎（参数化生成 Goal 骨架）
- `LOOP-05`: issue-fix 修复模板（滚动仓库上下文、版本修复知识）
- `LOOP-06`: pr-commit 模板（自动化代码整理、8 段式双语 PR 审查）
- `LOOP-07`: auto-research 模板（proposer -> executor -> evaluator 多轮收敛）
- `LOOP-08`: 自定义模板与模板市场扩展
- `LOOP-11`: Typed turn 决策枚举（route 与 result 判定）
- `LOOP-12`: Typed handoff packet（跨 agent/会话/团队成员交接封包）
- `LOOP-14`: 上下文智能剪枝（丢弃冗余历史，保留审计事实）
- `LOOP-15`: Checkpoint / Resume / Rewind 时间旅行机制
- `LOOP-16` / `SURF-10`: Goal 时间线视图与步骤卡片流
- `LOOP-17`: No-progress 断路器（防止死循环与额度黑洞）
- `LOOP-18` / `LOOP-19`: Stop Condition 验收与 Run Log 深度固化
- `LOOP-20`: Quota 占空比记账与能耗预算
- `LOOP-21`: 修复知识沉淀与 decision 谱系跟踪
- `SURF-09`: 团队长任务面板与模板运行视图

#### 涉及文件与模块
- 后端：`src/loopdesk/templates/` (新建), `src/loopdesk/engine/runner.py`, `src/loopdesk/engine/checkpoint.py`, `src/loopdesk/gateway/templates.py` (新建)
- 前端：`frontend/src/screens/TaskBoard.tsx`, `frontend/src/screens/TaskDetail.tsx`, `frontend/src/overlays/Modals.tsx`
- 测试：`tests/test_engine/test_templates.py`, `tests/test_engine/test_checkpoint.py`

#### 详细任务分解

##### Task F6.1: 模板引擎内核与参数化 Goal 骨架生成器 (LOOP-04, LOOP-08)
- **TDD 规格**：
  - 单元测试：`tests/test_engine/test_template_engine.py:test_render_goal_skeleton`
  - 定义模板 Schema：`TemplateManifest(id, name, version, inputs, steps, stop_conditions)`
  - 给定输入参数（如 `issue_url`, `branch_name`），渲染出五阶段（triage -> maker -> checker -> gate -> delivery）的标准 Goal 骨架
- **验证命令**：`pytest tests/test_engine/test_template_engine.py`

##### Task F6.2: issue-fix 标准模板与双分支隔离执行流 (LOOP-05, LOOP-18, LOOP-19)
- **TDD 规格**：
  - 集成测试：`tests/test_engine/test_issue_fix_flow.py:test_issue_fix_lifecycle`
  - 自动创建 `codex/issue-<id>-<slug>` 工作分支，拉取工单内容注入上下文；
  - 驱动 Maker 编写 failing test 并最小实现，驱动 Checker 收集证据并输出 Run Log；
  - 满足全部测试与 stop condition 后流转至待评审状态。
- **验证命令**：`pytest tests/test_engine/test_issue_fix_flow.py`

##### Task F6.3: pr-commit 模板与自动化 PR 封包审查 (LOOP-06, LOOP-21)
- **TDD 规格**：
  - 单元测试：`tests/test_engine/test_pr_commit_flow.py:test_generate_pr_review_packet`
  - 自动归纳分支提交集，生成符合 PRD §9.4 的 8 段双语 PR 描述（上下文、变更点、测试覆盖、风险评估等）；
  - 提取修复知识沉淀为决策记录谱系。
- **验证命令**：`pytest tests/test_engine/test_pr_commit_flow.py`

##### Task F6.4: auto-research 模板与多角色循环收敛 (LOOP-07, LOOP-11)
- **TDD 规格**：
  - 单元测试：`tests/test_engine/test_auto_research.py:test_proposer_executor_loop`
  - 实现提案者（Proposer）、执行者（Executor）、评估者（Evaluator）的角色轮转状态机；
  - 基于 Typed Turn 决策枚举控制循环迭代或收敛终止。
- **验证命令**：`pytest tests/test_engine/test_auto_research.py`

##### Task F6.5: 结构化 Handoff Packet、时间旅行与断路器 (LOOP-12, LOOP-14, LOOP-15, LOOP-17)
- **TDD 规格**：
  - 单元测试：`tests/test_engine/test_handoff_and_rewind.py:test_checkpoint_and_rewind`
  - 支持将运行状态压缩为可移植的 `HandoffPacket`（剥离冗余历史，保留 Goal、环境快照、关键证据）；
  - 实现 `rewind_to(step_id)` 时间旅行回滚；当连续 3 轮无新增证据或进展时触发 `no-progress breaker` 挂起任务。
- **验证命令**：`pytest tests/test_engine/test_handoff_and_rewind.py`

##### Task F6.6: WebUI Goal 时间线与模板启动面板 (LOOP-16, SURF-09, SURF-10)
- **UI 规格**：
  - 在新建任务弹窗中增加「长任务模板选择器」（支持普通任务、issue-fix、pr-commit、auto-research）；
  - 选中模板任务时，右栏抽屉展示 Goal 时间线步进卡片流（Plan -> Execute -> Audit -> Decision）。
- **验证命令**：`cd frontend && npm run build` 并在浏览器中验证模板选择与时间线展示。

---

### Feature F7: Git 原生团队 AI 资产市场与一键下发 (Git-native Team AI Asset Distributor)

**业务价值**：将 Rules、Specs、Skills、MCP 配置文件纳入 Git 仓库管理，提供本地可交互的资产市场，并支持一键将团队资产同步/下发到本地开发工作区，消除云端 SaaS 依赖。

#### 需求覆盖清单
- `ASSET-01`: 团队资产统一注册表（Rules/Specs/Skills/MCP 统一元数据）
- `ASSET-02`: Git 仓库共享通道（基于 git 原生通道的分发与版本化）
- `ASSET-03`: 下发 Distributor（一键将资产 push/link 至本地 `.agents/` 或 `.codex/`）
- `ASSET-04`: 资产版本管理、锁定、审计与回滚
- `ASSET-05`: 资产发现、分类检索与本地复用
- `ASSET-06`: Skill Engineering 标准规范（Trigger / Context / Workflow / Evaluation）
- `ASSET-07`: Skill 组织级分发（免安装、统一语义版本）
- `ASSET-08`: 细粒度分发范围控制（Role 角色匹配、Tag 订阅）
- `ASSET-09`: 声明式 Team Hooks 与 MCP 环境变量 `${VAR}` 注入
- `ASSET-10`: SessionStart 钩子自动 Pull 检查与同步
- `ASSET-11`: 资产复用度量与健康度评估
- `ASSET-12`: 成果交付物（Deliverables）共享机制
- `ASSET-13`: 资产真源与派生文件生成（保全本地定制）
- `ASSET-14`: 工作流状态机与回归守护
- `SURF-13`: WebUI 团队资产市场交互

#### 涉及文件与模块
- 后端：`src/loopdesk/assets/` (新建), `src/loopdesk/assets/registry.py`, `src/loopdesk/assets/distributor.py`, `src/loopdesk/gateway/assets.py` (新建)
- 前端：`frontend/src/screens/TeamAssets.tsx`, `frontend/src/overlays/Modals.tsx`, `frontend/src/lib/api.ts`
- 测试：`tests/test_assets/test_registry.py`, `tests/test_assets/test_distributor.py`, `tests/test_gateway/test_asset_routes.py`

#### 详细任务分解

##### Task F7.1: Git 原生资产注册中心与 Schema 校验 (ASSET-01, ASSET-02, ASSET-06)
- **TDD 规格**：
  - 单元测试：`tests/test_assets/test_registry.py:test_scan_and_validate_assets`
  - 扫描项目 `.agents/`、`docs/rules/`、`skills/` 目录，构建统一的 `AssetRegistry`；
  - 严密校验各类资产规范（如 Skill 的 frontmatter、MCP 配置合规性）。
- **验证命令**：`pytest tests/test_assets/test_registry.py`

##### Task F7.2: 团队资产下发引擎 (Distributor) 与本地目录同步 (ASSET-03, ASSET-07, ASSET-10)
- **TDD 规格**：
  - 单元测试：`tests/test_assets/test_distributor.py:test_distribute_asset_to_workspace`
  - 实现 Distributor 下发逻辑：支持软链接（Symlink）或副本分发至当前开发者工作区；
  - 支持在 Session 启动时检查上游 Git 仓库资产变更并提示同步。
- **验证命令**：`pytest tests/test_assets/test_distributor.py`

##### Task F7.3: 分发范围控制与环境变量安全注入 (ASSET-08, ASSET-09)
- **TDD 规格**：
  - 单元测试：`tests/test_assets/test_distributor.py:test_role_scope_and_env_injection`
  - 支持按开发者角色（如 `frontend`, `backend`, `tester`）与 Tag 进行资产匹配；
  - 解析 MCP 配置中的 `${ENV_VAR}` 占位符，安全关联系统环境变量，防止硬编码泄露。
- **验证命令**：`pytest tests/test_assets/test_distributor.py`

##### Task F7.4: 资产版本锁定、冲突检测与回滚守护 (ASSET-04, ASSET-13, ASSET-14)
- **TDD 规格**：
  - 单元测试：`tests/test_assets/test_distributor.py:test_version_pin_and_rollback`
  - 在 `LOOP-STATE.json` 中记录已下发资产的版本指纹（SHA-256）；
  - 当本地修改与团队资产冲突时，提供保留本地修改并标记派生状态的能力，支持一键回滚至锁定版本。
- **验证命令**：`pytest tests/test_assets/test_distributor.py`

##### Task F7.5: WebUI 资产市场全功能打通与下发操作联动 (SURF-13, ASSET-05, ASSET-11)
- **UI 规格**：
  - 将 `frontend/src/screens/TeamAssets.tsx` 由静态 Mock 升级为从 `/api/v1/assets` 动态拉取；
  - 激活「下发到工作区」交互动作，点击后调起分发确认弹窗，下发成功后卡片状态由「未安装」变为「已同步」，提供版本号与健康度标签。
- **验证命令**：启动 Gateway，通过 Playwright 自动化验证资产列表拉取与下发按钮交互。

---

### Feature F8: Local-first Agent 注册表与多 Runtime 编排调度 (Multi-agent Orchestration & Registry)

**业务价值**：允许在开发者本地机器上直接调度 Claude Code、Codex CLI、Pi 等多样化 Agent，基于任务复杂度与意图动态路由，提供 Worktree 并行分发和原生 PTY 终端保持。

#### 需求覆盖清单
- `ORCH-01`: 本地 Agent 注册表（Provider, Runtime, Instructions, Env, 最大并发）
- `ORCH-02`: Local-first 调度执行（完全在本地拉起，不替代原 Agent Runtime）
- `ORCH-03`: 意图路由 Task Router + 人工强制指定 (Human Override)
- `ORCH-04`: Per-Goal Worktree 隔离沙箱
- `ORCH-05`: 多 Agent 并行扇出与赢家选择 (Winner Selection)
- `ORCH-06`: 主会话与子会话平行探索（对抗性探索，结果可合并回主线）
- `ORCH-07`: Agent 状态向上 Rollup 汇报 (blocked/working/done/idle)
- `ORCH-08`: 原生 PTY 保留（不篡改、不粉饰底层终端真实流式输出）
- `ORCH-09`: Detach / Restore 与原生会话恢复
- `ORCH-10`: Session Host 权威不变量（单进程所有权，拒绝冲突并发）
- `ORCH-11`: Runtime Capability Profile 矩阵
- `ORCH-12`: 会话恢复自动保留工作目录 Workdir
- `ORCH-13`: Runtime Driver 驱动抽象层
- `SURF-03`: Agent Work Feed 动态流
- `SURF-04`: 统一运行视图

#### 涉及文件与模块
- 后端：`src/loopdesk/orchestrator/` (新建), `src/loopdesk/orchestrator/registry.py`, `src/loopdesk/orchestrator/router.py`, `src/loopdesk/orchestrator/pty_manager.py`
- 前端：`frontend/src/screens/SettingsAgent.tsx`, `frontend/src/screens/ControlCenter.tsx`, `frontend/src/components/ConversationDock.tsx`
- 测试：`tests/test_orchestrator/test_registry.py`, `tests/test_orchestrator/test_router.py`

#### 详细任务分解

##### Task F8.1: Agent 注册表与 Runtime Capability Profile (ORCH-01, ORCH-11, ORCH-13)
- **TDD 规格**：
  - 单元测试：`tests/test_orchestrator/test_registry.py:test_register_and_detect_agents`
  - 自动探测本地环境中可用的 CLI 运行时（如 `codex`, `claude`, `pi`）；
  - 构建 `AgentProfile(id, name, runtime, capability_matrix, max_concurrency)` 并持久化在本地配置中。
- **验证命令**：`pytest tests/test_orchestrator/test_registry.py`

##### Task F8.2: 意图驱动的任务路由器与人工覆盖 (ORCH-02, ORCH-03)
- **TDD 规格**：
  - 单元测试：`tests/test_orchestrator/test_router.py:test_route_task_by_intent`
  - 根据任务类型（代码修复、架构设计、文档调研）自动推荐最优 Agent；
  - 严格支持用户显式指定的 `preferred_agent` 覆盖系统推荐。
- **验证命令**：`pytest tests/test_orchestrator/test_router.py`

##### Task F8.3: Worktree 隔离沙箱与多 Agent 并行竞争 (ORCH-04, ORCH-05, ORCH-06)
- **TDD 规格**：
  - 集成测试：`tests/test_orchestrator/test_parallel.py:test_fanout_and_winner_selection`
  - 将同一复杂任务扇出（Fan-out）至 2 个不同的 Agent（如 Claude 与 Codex），各自在独立 Git Worktree 中运行；
  - 运行自动化测试对比结果指标，提示用户择优合并（Winner Selection）。
- **验证命令**：`pytest tests/test_orchestrator/test_parallel.py`

##### Task F8.4: 真实 PTY 进程托管、断连续跑与 Workdir 保留 (ORCH-08, ORCH-09, ORCH-10, ORCH-12)
- **TDD 规格**：
  - 单元测试：`tests/test_orchestrator/test_pty.py:test_pty_session_lifecycle`
  - 采用伪终端（PTY）拉起 Agent 进程，拦截并保留 ANSI 原生控制码；
  - 支持后台 Detach 与 Re-attach，进程恢复时自动恢复原工作目录与上下文。
- **验证命令**：`pytest tests/test_orchestrator/test_pty.py`

##### Task F8.5: WebUI Agent 编排配置与实时状态 Rollup (ORCH-07, SURF-03, SURF-04)
- **UI 规格**：
  - 将 `frontend/src/screens/SettingsAgent.tsx` 对接后端 Agent 配置端点，支持启用/停用特定 Agent 及调整并发限制；
  - 控制中心与任务详情实时展示各 Agent 的运行心跳与状态 Rollup 标签。
- **验证命令**：`cd frontend && npm run build` 验证编译与面板渲染。

---

### Feature F9: 外部系统双向集成与 MCP 连接器生态 (External Systems & MCP Bi-directional Sync)

**业务价值**：实现与 JIRA、Plane 工单系统的无缝拉取与双向回写，将 Confluence 知识空间即时转为 Agent 可索引的上下文，提供高内聚、热插拔、调用可追溯的 MCP 架构。

#### 需求覆盖清单
- `SYS-02`: ACP-second 适配层支持
- `SYS-03`: JIRA 连接器（工单拉取、状态推进、排查总结回写）
- `SYS-04`: Plane 连接器（开源任务系统双向对接）
- `SYS-05`: Confluence 连接器（项目知识空间索引与实时引用）
- `SYS-06`: GitHub 连接器（Issue / PR / Review 联动）
- `SYS-07`: 外部系统双向同步机制（Inbound 事件驱动 + Outbound 成果回写）
- `SYS-08`: 工作区级 MCP 生命周期治理（启用/禁用/重试/熔断/审计）
- `SYS-09`: MCP 工具调用全链路溯源（关联 Goal、Run、Approval、Token 成本）
- `SYS-10`: 可插拔连接器扩展（支持任意 stdio/SSE MCP Server 动态加载）
- `SYS-11`: 细粒度 MCP 关键字与意图路由

#### 涉及文件与模块
- 后端：`src/loopdesk/connectors/` (新建), `src/loopdesk/connectors/jira.py`, `src/loopdesk/connectors/plane.py`, `src/loopdesk/connectors/confluence.py`, `src/loopdesk/mcp/`
- 前端：`frontend/src/screens/SettingsMcp.tsx`, `frontend/src/overlays/Modals.tsx`
- 测试：`tests/test_connectors/test_jira.py`, `tests/test_connectors/test_mcp_lifecycle.py`

#### 详细任务分解

##### Task F9.1: JIRA 与 Plane 双向工单同步器 (SYS-03, SYS-04, SYS-07)
- **TDD 规格**：
  - 单元测试：`tests/test_connectors/test_ticket_sync.py:test_jira_and_plane_sync`
  - 模拟实现基于 JIRA/Plane REST API 的任务读取，将外部任务映射为 LoopDesk 本地 Task 模型；
  - 任务在本地「已完成」或审批通过后，自动调用 API 回写外部工单状态与 PR 链接。
- **验证命令**：`pytest tests/test_connectors/test_ticket_sync.py`

##### Task F9.2: Confluence 知识空间索引与 Prompt 注入 (SYS-05, SYS-06)
- **TDD 规格**：
  - 单元测试：`tests/test_connectors/test_knowledge_sync.py:test_confluence_indexer`
  - 拉取指定 Confluence 空间文档，生成本地 Markdown 缓存与关键词倒排索引；
  - Agent 执行时按任务关键词自动检出相关知识片段并注入上下文。
- **验证命令**：`pytest tests/test_connectors/test_knowledge_sync.py`

##### Task F9.3: MCP 连接器热插拔与生命周期守护 (SYS-08, SYS-10)
- **TDD 规格**：
  - 单元测试：`tests/test_mcp/test_lifecycle.py:test_mcp_hot_reload_and_circuit_breaker`
  - 动态拉起基于 stdio 或 SSE 的 MCP Server 进程；
  - 当连接器发生连续 3 次超时或崩溃时，触发健康熔断，自动降级并不影响主进程。
- **验证命令**：`pytest tests/test_mcp/test_lifecycle.py`

##### Task F9.4: MCP 工具调用审计溯源与关键字路由 (SYS-09, SYS-11, SYS-02)
- **TDD 规格**：
  - 单元测试：`tests/test_mcp/test_traceability.py:test_tool_call_trace`
  - 拦截每一次 MCP 工具调用，记录 `call_id`, `tool_name`, `input_params`, `latency_ms`, `token_cost`；
  - 将调用证据结构化落盘至对应的 Run Log。
- **验证命令**：`pytest tests/test_mcp/test_traceability.py`

##### Task F9.5: WebUI MCP 连接器配置中心与实时状态测试 (SettingsMcp)
- **UI 规格**：
  - 将 `frontend/src/screens/SettingsMcp.tsx` 对接后端连接器管理接口；
  - 支持在界面上手动添加新 MCP Server（配置 command, args, env），并提供「测试连接」按钮实时反馈健康状态。
- **验证命令**：`cd frontend && npm run build` 验证前端配置界面。

---

### Feature F10: 团队级治理、多级审批门禁、安全护栏与记忆提炼 (Governance, Safety Guardrails & Memory Distillation)

**业务价值**：构建满足小型团队与企业合规要求的治理体系，提供五级审批门、五层安全语法、Token 配额熔断，以及团队可共享、本地可编辑、自动提炼的三层记忆系统。

#### 需求覆盖清单
- **审批门与验证**：`LOOP-09` (Quota 准跑判定), `LOOP-10` (五级 Gate), `LOOP-13` (独立验证机制), `GOV-15` (Validation Receipt 机器可读验证凭证), `GOV-16` (审计控制头契约)
- **安全与权限**：`GOV-06` (权限模式), `GOV-07` (沙箱), `GOV-08` (Deny-wins 工具策略与路径黑名单), `GOV-09` (五层安全语法: IPC/fs/net/secret/pty), `GOV-10` (Secrets 保护), `GOV-11` (Hash-chain 审计日志), `GOV-12` (失败模式目录与降级), `WS-08` (公私边界划分)
- **团队配额与状态**：`GOV-02` (成本跟踪 Rollup), `GOV-03` (预算硬上限与 Kill-switch), `GOV-13` (团队额度管理), `GOV-14` (Cloud API Key 额度预留), `WS-05` (团队级 Workspace State), `WS-06` (Handoff 封包), `WS-07` (部分导出/导入), `WS-09` (白盒人类可读状态)
- **三层记忆与上下文**：`CTX-01` (上下文注入契约), `CTX-02` (跨会话连续性), `CTX-03` (跨团队上下文引用), `CTX-04` (Big @ 跨 Agent 引用), `CTX-05` (代理借用), `CTX-06` (短期/长期/团队三层记忆), `CTX-07` (白盒可编辑记忆), `CTX-08` (Memory Dream 后台提炼), `CTX-09` (记忆条目 Schema), `CTX-10` (智能压缩与过期消除), `CTX-11` (Human Model), `CTX-12` (本地检索), `CTX-13` (按成员隔离记忆)
- **持续学习与用户面**：`LEARN-01` ~ `LEARN-08` (持续学习循环、KB Health、摩擦信号沉淀、决策谱系), `SURF-05` (IM 远程接入预留), `SURF-07` (引导式 Onboarding), `SURF-08` (机器可读 `/llms.txt`), `SURF-11` (Diff 注释回传)

#### 涉及文件与模块
- 后端：`src/loopdesk/governance/` (新建), `src/loopdesk/memory/`, `src/loopdesk/security/`, `src/loopdesk/gateway/governance.py` (新建)
- 前端：`frontend/src/screens/ControlCenter.tsx`, `frontend/src/screens/SettingsOther.tsx`
- 测试：`tests/test_governance/`, `tests/test_memory/`

#### 详细任务分解

##### Task F10.1: 五级审批门禁体系与 Validation Receipt 独立凭证 (LOOP-09, LOOP-10, LOOP-13, GOV-15, GOV-16)
- **TDD 规格**：
  - 单元测试：`tests/test_governance/test_gates.py:test_five_tier_gates_and_receipt`
  - 实现五级 Gate 校验链：
    1. Health Gate（基础环境正常）
    2. Operator Gate（人工裁决确认）
    3. Evidence Gate（必须具备测试/构建等强证据）
    4. Focus Gate（变更文件未越界）
    5. Quota Gate（未超配额）
  - 校验通过后生成带有数字签名/哈希摘要的 `ValidationReceipt`。
- **验证命令**：`pytest tests/test_governance/test_gates.py`

##### Task F10.2: 五层安全语法与公私边界隔离 (GOV-08, GOV-09, GOV-10, WS-08)
- **TDD 规格**：
  - 单元测试：`tests/test_governance/test_security_policy.py:test_five_layer_security`
  - 落实对 IPC、文件系统（`.env`/私钥只读或拦截）、网络访问、Secret 脱敏和终端转义字符的五层规则检查；
  - 确保私有环境配置与凭证绝不泄露到 Git 共享区或导出文件中。
- **验证命令**：`pytest tests/test_governance/test_security_policy.py`

##### Task F10.3: 团队配额治理、成本 Rollup 与硬熔断机制 (GOV-02, GOV-03, GOV-13)
- **TDD 规格**：
  - 单元测试：`tests/test_governance/test_quota.py:test_quota_limits_and_kill_switch`
  - 实时汇总各 Agent/任务消耗的 Token 与预估成本；
  - 达到单日或项目预算阈值时，自动拒绝新的执行轮次，触发安全挂起。
- **验证命令**：`pytest tests/test_governance/test_quota.py`

##### Task F10.4: 三层记忆模型、Memory Dream 提炼与本地检索 (CTX-01, CTX-06, CTX-07, CTX-08, CTX-09, CTX-12)
- **TDD 规格**：
  - 单元测试：`tests/test_memory/test_three_tier_memory.py:test_memory_dream_distillation`
  - 实现短期运行记忆、长期项目记忆与团队共用记忆分层存储；
  - 后台任务 `Memory Dream` 定期对过往 Run Log 中的摩擦点和成功案例进行摘要提炼，生成白盒可编辑的 `.md` 知识沉淀。
- **验证命令**：`pytest tests/test_memory/test_three_tier_memory.py`

##### Task F10.5: 跨团队上下文传递、Big @ 引用与 Handoff 封包 (CTX-03, CTX-04, WS-05, WS-06)
- **TDD 规格**：
  - 单元测试：`tests/test_memory/test_cross_context.py:test_big_at_reference`
  - 支持在 Prompt 中使用 `@agent/name` 或 `@project/artifact` 跨界拉取上下文；
  - 结构化封包输出完整交接材料，支持其它成员开箱即用。
- **验证命令**：`pytest tests/test_memory/test_cross_context.py`

##### Task F10.6: 循环反馈归因与持续学习沉淀引擎 (LEARN-01 ~ LEARN-08)
- **TDD 规格**：
  - 单元测试：`tests/test_memory/test_learning.py:test_continuous_learning_flush`
  - 监控任务失败与人工驳回信号，自动分析归因并沉淀入测试规则或 Agent 建议清单；
  - 维护本地知识库健康度评分（KB Health）。
- **验证命令**：`pytest tests/test_memory/test_learning.py`

##### Task F10.7: WebUI 治理控制中心与交互式引导 (ControlCenter, SURF-07, SURF-08)
- **UI 规格**：
  - 升级 `frontend/src/screens/ControlCenter.tsx`，将静态指标替换为真实的系统健康度、Token 消耗走势、熔断告警与审批队列概览；
  - 支持展示机器可读入口 `/llms.txt`。
- **验证命令**：`cd frontend && npm run build` 验证控制中心渲染。

---

## 3. 验收与回滚标准（Acceptance & Rollback Criteria）

### 3.1 验收标准（Acceptance Criteria）
1. **PRD 需求 100% 覆盖**：PRD §9.1 ~ §9.9 的 119 项功能需求均拥有对应的 Task、测试用例与验证闭环。
2. **测试驱动开发（TDD）先行**：每一个 Task 必须编写对应的失败测试并确认红灯，随后编写最小实现使其绿灯通过。
3. **前端 0 报错构建**：所有 UI 面板（模板面板、资产市场、Agent 设置、MCP 设置、控制中心）改动必须保证 `cd frontend && npm run build` 严格 0 警告 0 报错。
4. **定位与命名合规**：绝不泄露任何废弃概念（无个人版/独立开发者叙事，无旧产品名泄露），全面对齐 v2.0 团队循环工作区规范。

### 3.2 回滚标准（Rollback Criteria）
1. 若新引入的模板或资产下发破坏了既有 `LOOP-STATE.json` 兼容性，立即通过 Git 版本回滚至前序提交。
2. 若任何安全护栏或 Gate 校验存在漏判风险，暂停对应 Task 合流，降级至严格的人工审核模式。
