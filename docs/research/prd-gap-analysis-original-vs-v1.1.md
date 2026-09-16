# PRD Gap Analysis — Original LoopDesk PRD vs Current PRD v1.1

> Status: Draft for review
> Owner: Product / Engineering
> Last updated: 2026-07-28
> Input: 原始 PRD 材料、`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/prd/personal-loop-workspace.md`、`docs/features/core-feature-list.md`

## 1. 分析说明

本文档用于对照：
- 原始 LoopDesk PRD 材料中的产品定义、模块划分、MVP 范围、用户角色、架构设想
- 当前最新 PRD：`docs/prd/personal-loop-workspace-v1.1.zh.md:1`

目标不是推翻 v1.1，而是识别：
- 哪些原始需求已被覆盖
- 哪些原始需求被降级 / 延后 / 未显式纳入
- 哪些原始表达需要保留为可追溯缺口或后续规划项

## 2. 已覆盖或已收敛的内容

| 原始 PRD 概念 | 当前 PRD v1.1 状态 | 说明 |
| --- | --- | --- |
| Local-first 个人工作空间 | 已覆盖 | 明确为本地 workspace、`LOOP-STATE.json`、local-first，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:117` |
| 多工具 / 多 Agent 协同 | 已覆盖 | Cross-tool integration、MCP-first、ACP-second，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:121` |
| Workspace 作为长期上下文载体 | 已覆盖 | Workspace State Protocol、memory、skills、artifacts，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:137` |
| Loop Engine / 持续执行 | 已覆盖 | Loop Engine、triage、maker/checker、run log、stop condition，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:138` |
| Skill / MCP 扩展 | 已覆盖 | Skills、MCP、extensions，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:305` 与 `docs/prd/personal-loop-workspace-v1.1.zh.md:310` |
| Web UI / CLI 主控制面 | 已覆盖 | Runtime Visibility and Control、Web Surface，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:376` |
| IM 远程控制 | 已覆盖 / 延后 | IM Remote Control 仍在 v0.2，未在 v1.1 升为主叙事，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:170` 与 `docs/prd/personal-loop-workspace-v1.1.zh.md:397` |
| 工作流、记忆、审批、成本 | 已覆盖 | Memory、Safety and Cost、approvals、observability，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:293` 与 `docs/prd/personal-loop-workspace-v1.1.zh.md:315` |

## 3. 未实现或未被充分纳入 PRD v1.1 的内容

### 3.1 产品叙事层缺口

| 原始 PRD 概念 | 当前状态 | 差距说明 |
| --- | --- | --- |
| **Harness 作为一等概念** | 未显式保留 | v1.1 已收敛为 Control Plane，Harness 不再是显式模块名；若团队仍用该词沟通，需要术语映射，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:36` |
| **Personal Super Agent** | 已收敛 | v1.1 更强调 Control Plane / Agent Continuity，弱化“超级 Agent”包装，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:60` |
| **Intent Engine / 意图理解层** | 未显式纳入 | 原始 PRD 有独立 Intent Engine；v1.1 目前由 triage / context assembly / Loop Engine 隐式承担，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:285` |
| **Task Planner 作为显式模块** | 未独立成节 | 原始 PRD 有 Task Planner 模块；v1.1 主要落到 Loop/Goal 模型与 workflow orchestration，缺少显式 planner 责任边界，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:274` |
| **Continuous Learning Loop** | 未显式命名 | 当前 PRD 有 memory、skill reuse、run log，但没有显式 Continuous Learning Loop 作为产品能力名，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:293` |
| **多角色 Persona 体系** | 收窄 | v1.1 主要围绕 independent developer，未保留知识工作者、技术负责人等扩展 persona，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:76` |

### 3.2 功能模块层缺口

| 原始模块 | 当前 PRD v1.1 覆盖情况 | 建议后续处理 |
| --- | --- | --- |
| 模块一：Workspace 上下文系统 | 部分覆盖 | 已有 workspace state，但缺少显式 context 子结构：`user.md`、`project.md`、`task_context.md` 级组织，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:269` |
| 模块二：Agent Harness 运行时 | 已映射为 adapter/runtime | 无统一 `AgentRuntime` 接口显式定义；当前依赖 CLI/MCP/ACP adapter 分散实现，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:263` |
| 模块三：ACP Agent 调用层 | 部分覆盖 | 已有 ACP-second，但缺少显式 ACP Gateway、discovery、context injection、state sync 的独立规格，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:280` |
| 模块四：IM 远程控制系统 | 延后到 v0.2 | 原始 PRD 将飞书/微信/QQ/钉钉列为 MVP；v1.1 仍为 optional continuation surface，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:170` |
| 模块五：MCP Tool 系统 | 已覆盖 | MCP 作为核心能力保留，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:310` |
| 模块六：Skill 系统 | 已覆盖 | 但 v1.1 额外引入 Skill Engineering 约束，较原始 PRD 更严格，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:305` |
| 模块七：智能工具路由 | 未显式纳入 | 原始 PRD 有独立 Router；v1.1 无显式智能路由模块，只有 provider/model 使用，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:280` |
| 模块八：智能意图识别 | 未显式纳入 | 当前由 triage / context assembly 隐性承担，缺少独立 intent classification 设计，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:285` |
| 模块九：任务拆解 Engine | 部分覆盖 | Loop/Goal 承担部分职责，但缺少显式 DAG/task graph / agent assignment 模块，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:274` |

### 3.3 数据模型层缺口

| 原始 PRD 数据模型 | 当前 PRD v1.1 | 差距 |
| --- | --- | --- |
| Workspace 类型：Project / Personal / Business | 未显式保留 | 当前主要围绕 project/loop/goal，缺少 workspace type 分类，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:269` |
| Workspace 目录结构：`context/`、`tasks/`、`memory/`、`skills/`、`tools/`、`agents/`、`logs/` | 未显式保留 | 当前核心是 `.loopdesk/` + `LOOP-STATE.json`，但未显式定义这些子目录规范，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:269` |
| Task 数据模型 | 部分覆盖 | 有 Loop/Goal/Task 概念，但无显式 Task JSON schema / execution trace schema，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:274` |
| Execution Trace | 部分覆盖 | 有 run log，但未定义独立 Execution Trace 数据模型，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:293` |
| Agent Runtime 抽象接口 | 未显式保留 | 原始 PRD 有统一接口；v1.1 没有显式接口定义，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:263` |
| Context 子模型：user / project / task | 未显式保留 | 当前 PRD 强调 durable state，但未显式拆分三类 context 文件 / 结构，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:269` |

### 3.4 用户角色与场景层缺口

| 原始 PRD 角色/场景 | 当前 PRD v1.1 | 差距 |
| --- | --- | --- |
| AI 增强开发者 | 已覆盖 | 主要用户匹配，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:78` |
| 技术负责人 | 未保留 | v1.1 未显式纳入技术负责人 persona |
| 知识工作者 | 未保留 | v1.1 未显式纳入知识工作者 persona |
| 信息收集 / 分析 / 写作 / 自动执行流程 | 未显式覆盖 | v1.1 更偏向 coding agent 工作流，未保留通用知识工作流场景，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:85` |

### 3.5 MVP 范围层缺口

| 原始 V1.0 MVP | 当前 PRD v1.1 状态 | 说明 |
| --- | --- | --- |
| Local Workspace | 已实现 / 已规划 | v0.1 已有，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:505` |
| Context 管理 | 部分实现 | 有 memory/state，但缺显式 context 子结构 |
| Task 管理 | 部分实现 | 有 Loop/Goal/Task，但缺显式 task planner / task graph |
| ACP 调用 Claude Code | 已覆盖 | ACP-second，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:280` |
| ACP 调用 Codex CLI | 已覆盖 | Tool-specific adapters，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:280` |
| OpenCode 支持 | 未显式纳入 | v1.1 枚举了 Claude Code、Codex、Codebuddy、Trae、Gemini；OpenCode 不在显式列表中，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:22` |
| MCP Client | 已覆盖 | MCP-first，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:310` |
| Skill Registry | 已覆盖 | Skills，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:305` |
| Web UI | 已覆盖 | Local Web UI，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:376` |
| 飞书机器人 | 延后到 v0.2 | IM adapter 仍为 v0.2，未纳入 v1.1 核心，见 `docs/prd/personal-loop-workspace-v1.1.zh.md:397` |

## 4. 建议的后续动作

### 4.1 必须补齐的 PRD 映射
- 显式新增 `Intent / Task Planner` 责任边界，或说明该能力由 `Loop Engine + triage` 承担。
- 显式定义 `context/` 子结构或等价 schema：user / project / task context。
- 明确是否保留 OpenCode 作为 v1.x 支持 runtime。
- 明确是否保留 Business/Personal Workspace type 分类，或继续收窄为 project-only。

### 4.2 建议纳入 v1.1/v1.2 的缺口
- Agent Runtime 抽象接口
- Execution Trace / Run Log 更显式 schema
- 智能路由能力边界
- 多 persona 支持范围
- 知识工作者场景是否进入 v1.x

### 4.3 明确延后项
- IM 全平台：飞书/微信/QQ/钉钉
- 云端 sync / Business Workspace / multi-tenant
- 自研模型
- 显式 Continuous Learning Loop 若不在 v1.x，需在 roadmap 中单列

## 5. 结论

当前 PRD v1.1 在 Control Plane、Agent Continuity、Loop Engine、Skills/MCP、local-first 安全边界上已经明显收敛并强于原始 PRD。

但仍存在一批原始 PRD 概念未被显式纳入，主要集中在：
- Intent / Task Planner 模块化表达
- Context 子结构
- OpenCode 支持
- 多 persona / 知识工作场景
- 显式 router / execution trace / agent runtime interface

建议在 v1.1 评审时逐项确认：
1. 保留为显式需求
2. 由现有模块隐性承担
3. 延后到 v1.2/v2.0
4. 主动放弃以避免范围膨胀
