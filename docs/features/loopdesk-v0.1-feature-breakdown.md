# LoopDesk v0.1 Feature Breakdown

> Status: ready for review
> Version: v0.1
> Date: 2026-07-07
> Owner: Product / Engineering
> Inputs: `docs/prd/personal-loop-workspace.md`, `docs/decisions/product-strategy.md`, `docs/plans/2026-07-07-loopdesk-implementation-plan.md`, `docs/decisions/risk-handling-plan.md`

## 1. Breakdown Principle

- Feature boundaries follow **personal developer workflow**, not UI screens.
- `Loop` and `Goal` are **backend orchestration boundaries**.
- The frontend should present **one continuous workflow** from discovery to execution.
- Developer intervention is required only at **approval, escalation, ambiguity, denylist, high risk, or insufficient budget/permission**.

## 2. Feature Summary

| ID | Feature | Priority | Boundary Note |
| --- | --- | --- | --- |
| F1 | Personal Loop Workspace Foundation | Must | state, layout, template runtime, workspace initialization |
| F2 | Unified Workflow Surface | Must | backend `Loop/Goal` boundary + frontend continuous task flow |
| F3 | Cross-Tool Adapter and Bridge | Must | MCP-first, ACP-second, local CLI bridge, event/state translation |
| F4 | Memory, Skills, and Reusable Templates | Must | durable memory, session continuity, personal workflow templates |
| F5 | Cost Observatory and Safety Guard | Must | budget, approval, escalation, denylist, kill switch, worktree cleanup |
| F6 | Verification, Documentation, and Release Gates | Must | integration tests, docs checklist, boundary checks, public-surface validation |

## 3. Feature Details

### F1：Personal Loop Workspace Foundation

**目标**：建立个人开发者的最小 loop workspace 底座，让状态、目录、模板 runtime 可初始化、可恢复、可审计。

**范围**
- in：`LOOP-STATE.json` schema、序列化、目录布局、worktree helper、模板目录与注册元数据
- out：多渠道推送、团队 workspace、云房间、marketplace

**验收条件**
- `LOOP-STATE.json` 可创建、读取、更新、导出、恢复
- 默认目录包含 `memory`、`skills`、`artifacts`、`worktrees`、`personal_templates`
- 新建 workspace 时可选用个人 workflow template
- 自动化 Goal 可在独立 worktree 中启动，且不会污染主分支
- 定向测试通过

**边界说明**
- 这是 backend-owned foundation。
- 前端只展示 workspace 状态、目录健康度、template 选用结果，不暴露 legacy `session` 或 `workspace-state.json` 作为主状态。

---

### F2：Unified Workflow Surface

**目标**：让个人开发者始终看到同一个连续开发过程，而不是两个割裂的“Loop 页面”和“Goal 页面”。

**范围**
- in：CLI、Gateway RPC、本地 Web UI、`工作台` 主视图、run log、approval、cost、next-action 展示
- out：多渠道通知、团队权限、复杂 dashboard、heavy desktop GUI

**验收条件**
- CLI 可初始化 workspace、查看当前工作流、Loop/Goal 状态、运行日志、审批项、成本摘要
- WebUI 以 `工作台` 为主入口，统一展示当前任务/Goal、来源 Loop、run log、approval、cost、模板建议、下一步操作
- `运行中心` 展示 Goal 运行历史、maker/checker 结果、escalation、错误与重试
- 静态资源与 RPC 结构通过 focused tests 校验
- 不暴露 legacy channel/scheduler 入口

**边界说明**
- `Loop` 和 `Goal` 是 backend orchestration，不是前端两张独立页面。
- 用户不需要手动“从 Loop 切到 Goal”；系统在 backend 自动衔接，前端只展示当前工作流状态。

---

### F3：Cross-Tool Adapter and Bridge

**目标**：至少打通一个本地编码工作流，并把工具事件与 loop state 双向同步。

**范围**
- in：MCP adapter、ACP-second placeholder、本地 CLI bridge、tool event -> `LOOP-STATE.json` 映射
- out：云端同步、重型 vendor 私有协议、多渠道 bridge

**验收条件**
- 至少一个本地 coding workflow 可通过 MCP 与 LoopDesk 联动
- tool 输入/输出可正确写入 `LOOP-STATE.json` 的 run log / artifacts / goal context
- 本地 bridge 能手动触发外部工具并把结果回填，供后续 Loop/Goal 使用
- 前后端呈现为连续任务流

**边界说明**
- adapter 负责把外部工具结果翻译成 workspace state，但不负责把前端页面改成 tool-first 多入口。
- backend 根据 state 自动决定继续 discovery、triage 还是 bounded Goal 执行。

---

### F4：Memory, Skills, and Reusable Templates

**目标**：把跨会话知识沉淀进个人 memory、reusable skills 和 workflow templates，降低 intent debt。

**范围**
- in：durable memory、搜索、compaction、session resume、skills/meta-skills 查看与运行、个人模板查看与审计
- out：marketplace、云共享 skill、team knowledge base、team template management

**验收条件**
- 长会话可 compact，且关键知识可检索
- session 可 resume、export、abort
- skill 与 workflow template 可查看、运行、审计
- template 可被 Loop 选用，也可被 Goal 继承上下文
- memory/skills/templates 可在 WebUI 中查看，不强制团队化

**边界说明**
- templates 是 personal workflow runtime，不是 team asset store。
- LoopDesk 允许 template 被 backend loop/goal 选用，但不要求前端提供复杂 marketplace。

---

### F5：Cost Observatory and Safety Guard

**目标**：让 loop/goal 自动化可控、可审计、可停止，并把 `loop-engineering` 的安全运营规则本地化为个人工作台规则。

**范围**
- in：token/cost tracking、budget cap、approval queue、escalation、worktree cleanup/retain、run log、denylist、human gate、kill switch
- out：复杂企业权限、多云计费、团队审批流、team notification、cloud-first governance

**验收条件**
- 预算、审批、错误、升级路径、run log 都可在本地观察到
- 超过预算/denylist/repeated failure 时可切 report-only 或暂停 loop
- 高风险操作可阻止或升级给人
- 自动运行后的 worktree 可清理或保留快照
- 每个 Goal 结束后保留最少必要运行记录，支持复盘和后续 Loop

**边界说明**
- cost/safety 是 backend enforcement layer。
- 前端只展示可观察的成本、审批和升级状态，不提供 team governance 配置流。

---

### F6：Verification, Documentation, and Release Gates

**目标**：验证 v0.1 可发布的最小可用集合，并确保 docs、CLI、WebUI 口径一致。

**范围**
- in：定向集成测试、文档 checklist、发布验证、边界 grep 检查、README/product docs 口径收口
- out：团队功能、渠道落地页、营销素材

**验收条件**
- 所有 loop workspace 定向测试通过
- 至少一个 MCP 本地编码工作流跑通
- 至少一个个人 workflow template 可从 Loop 选用并继承上下文到 Goal
- 文档覆盖安装、连接工具、运行 loop、检查状态、失败恢复
- 公开 docs/CLI/Web UI 口径一致，无 legacy channels/media skills/team collaboration 泄露

**边界说明**
- 这是 release 边界 feature，不是新增产品能力。
- 验证重点是：backend `Loop/Goal` 边界、frontend continuous workflow 表达、legacy surface 隔离。

## 4. Execution Boundary Reminder

- `Loop` = backend discovery/triage/state maintenance
- `Goal` = backend bounded execution/verification
- Frontend = continuous workflow surface, approval/escalation entry point, observability
- v0.1 excludes: team rooms, channel-first onboarding, marketplace, heavy desktop GUI, cloud sync as core requirement

## 5. Next Step

Approval后，按 `docs/plans/2026-07-07-loopdesk-implementation-plan.md` 的 Goal 1-10 顺序进入 FDD + TDD 实现。
