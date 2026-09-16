# LoopDesk v1.2 Gap Backlog

> Status: Draft for grooming
> Owner: Product / Engineering
> Last updated: 2026-07-28
> Input: `docs/research/prd-gap-analysis-original-vs-v1.1.md:1`

## 1. 使用说明

本 backlog 只承接 **原始 PRD 与当前 PRD v1.1 之间的差距**，不新增与 v1.1 无关的产品方向。

每个 backlog item 至少包含：
- 为什么存在
- v1.1 的当前处理方式
- 建议优先级
- 最小可验收定义
- 决策问题

## 2. Backlog Items

### B1 — 显式 Intent / Task Planner 边界

- Gap 来源：原始 PRD 有独立 `Intent Engine` 与 `Task Planner`；v1.1 主要由 triage / context assembly / Loop Engine 隐性承担
- v1.1 现状：没有独立 planner 责任边界，也没有显式 intent classification 设计
- 建议优先级：P1
- 建议目标版本：v1.2
- 最小可验收定义：
  1. 在 PRD / 架构中明确 intent 与 planner 的职责边界
  2. 说明 triage 与 planner 的输入输出关系
  3. 明确该能力是产品层语义还是可复用实现模块
- 决策问题：
  - 是否把 planner 做成独立 service？
  - 是否允许 planner 产出 DAG 而非线性 todo？

### B2 — Context 子结构：`user.md` / `project.md` / `task_context.md`

- Gap 来源：原始 PRD 显式拆分三类 context；v1.1 目前是 durable state，但缺少显式子结构
- v1.1 现状：memory / state 已存在，但没有显式 context schema 或目录约定
- 建议优先级：P1
- 建议目标版本：v1.2
- 最小可验收定义：
  1. 定义三类 context 的最小字段和落盘位置
  2. 说明三类 context 与 `LOOP-STATE.json` 的关系
  3. 支持 context compaction / prune，避免无限膨胀
- 决策问题：
  - context 是文件还是 state 内嵌字段？
  - user/project/task context 的编辑权限是否不同？

### B3 — Agent Runtime 抽象接口

- Gap 来源：原始 PRD 有统一 `AgentRuntime` 接口；v1.1 目前是分散的 CLI/MCP/ACP adapter
- v1.1 现状：adapter 能力存在，但没有统一接口文档或接口测试锚点
- 建议优先级：P2
- 建议目标版本：v1.2
- 最小可验收定义：
  1. 文档化最小 runtime 接口：execute / resume / status / cancel / inspect
  2. 明确接口是“实现约束”还是“集成契约”
  3. 至少覆盖 Claude Code、Codex、Gemini 三类 runtime 的映射
- 决策问题：
  - 是否把接口只作为适配器开发文档，不强制 runtime 按接口重写？
  - 是否支持 runtime capability profile 动态发现？

### B4 — 显式 Execution Trace / Run Log Schema

- Gap 来源：原始 PRD 有 Execution Trace；v1.1 有 run log，但没有独立 schema
- v1.1 现状：run log 主要用于展示与诊断，缺少结构化字段和消费者接口
- 建议优先级：P2
- 建议目标版本：v1.2
- 最小可验收定义：
  1. 定义 trace/run log 的最小字段：action、tool、runtime、duration、cost、decision、result、artifacts
  2. 支持按 Goal / Loop / time range 查询
  3. 支持 replay / export 消费
- 决策问题：
  - trace 是否计入 durable source of truth？
  - 是否支持 selective retention / 自动压缩？

### B5 — 显式智能路由边界

- Gap 来源：原始 PRD 有独立 Router；v1.1 只有 provider/model 路由，没有显式任务级 router
- v1.1 现状：由 triage / context assembly 隐性决定执行路径
- 建议优先级：P2
- 建议目标版本：v1.2
- 最小可验收定义：
  1. 明确 router 的输入：intent、context、runtime capability、cost/safety policy
  2. 明确 router 的输出：runtime、skill、MCP tool、是否需要人工 approval
  3. 保留人工可干预点，不允许全自动 unbounded routing
- 决策问题：
  - router 是否面向开发者配置，还是面向 skill/meta-skill 封装？
  - 是否允许 runtime fallback 链？

### B6 — OpenCode 支持决策

- Gap 来源：原始 PRD 将 OpenCode 列为 MVP runtime；v1.1 显式枚举中未包含 OpenCode
- v1.1 现状：Claude Code、Codex、Codebuddy、Trae、Gemini 在叙事中更突出
- 建议优先级：P3
- 建议目标版本：v1.2+
- 最小可验收定义：
  1. 明确 OpenCode 是否进入官方支持矩阵
  2. 若进入，定义最小 adapter 行为和测试范围
  3. 若不进入，在 PRD 中显式说明排除原因
- 决策问题：
  - OpenCode 作为通用 runtime，还是仅保留 MCP 兼容路径？
  - 社区贡献 vs 官方支持？

### B7 — 多 Persona / 知识工作场景

- Gap 来源：原始 PRD 包含技术负责人、知识工作者及通用知识工作流；v1.1 主要收窄为 independent developer
- v1.1 现状：coding agent 工作流是主线，通用知识工作流未显式纳入
- 建议优先级：P3
- 建议目标版本：v1.2+
- 最小可验收定义：
  1. 明确 v1.x 主线 persona 边界
  2. 若扩展，给出最小第二 persona 模板与场景
  3. 避免把知识工作流做成 broad media/team creator surface
- 决策问题：
  - 是否允许 personal knowledge / writing / research loop，但不做 rich media？
  - 是否只通过 skill/template 表达 persona 差异，而不做用户 profile system？

### B8 — Workspace Type 分类

- Gap 来源：原始 PRD 有 Project / Personal / Business workspace；v1.1 主要围绕 project/loop/goal
- v1.1 现状：目录和 state 模型以 project workspace 为主
- 建议优先级：P3
- 建议目标版本：v1.2+
- 最小可验收定义：
  1. 明确是否保留 workspace type 字段
  2. 若保留，定义 type 对 template、memory、skills、isolation 的影响
  3. 若不保留，在 PRD 中说明未来可通过 project metadata 表达
- 决策问题：
  - workspace type 是产品层分类还是实现层 tag？
  - 是否允许同一台机器存在多个 type 的 workspace？

### B9 — 显式子目录规范

- Gap 来源：原始 PRD 有 `context/`、`tasks/`、`memory/`、`skills/`、`tools/`、`agents/`、`logs/`
- v1.1 现状：核心是 `.loopdesk/` + `LOOP-STATE.json`，未显式定义这些子目录
- 建议优先级：P3
- 建议目标版本：v1.2+
- 最小可验收定义：
  1. 明确保留目录还是仅保留 state 文件
  2. 若保留目录，定义最小目录契约和与 state 的一致性规则
  3. 说明目录是用户可浏览接口，还是内部实现
- 决策问题：
  - 是否允许 `.loopdesk/` 之外仍有 project assets？
  - 是否需要 tool-agnostic directory contract？

## 3. Backlog 优先级说明

- **P1**：会直接影响 v1.2 的产品叙事或实现边界，建议在 v1.1 review 后尽快确认
- **P2**：影响架构清晰度和后续工程效率，建议纳入 v1.2 architecture spike
- **P3**：有价值，但不阻塞 v1.2 主线；可作为 optional enhancement 或社区反馈驱动

## 4. Gating Rules

进入 v1.2 开发前，建议先完成：
1. `docs/decisions/prd-v1.1-review-checklist.md` 中的所有必选项结论
2. 每个 P1/P2 backlog item 的决策问题答案
3. 与 v1.1 的冲突检查，避免 v1.2 再次引入已放弃的范围

## 5. v1.2 当前进展

- 当前分支：`feat/loopdesk-v12-intent-planner-and-runtime-contracts`
- 已推进：B1/B2/B3/B4/B5 的 P1/P2 主线和首批测试已落地
- 当前 gate：`pytest -q tests/test_engine/test_router_decision.py tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_layout.py tests/test_loop_workspace/test_service.py tests/test_loop_workspace/test_runtime_matrix.py tests/test_gateway/test_rpc_sessions_v12.py tests/test_gateway/test_readiness.py tests/test_docs_guardrails.py tests/test_release_acceptance.py` 为 21 passed
- 已修复：`src/loopdesk/gateway/rpc_sessions.py:7` 缺少 `json` import；`tests/test_gateway/test_rpc_sessions_v12.py:13` fake runtime 缺少可查询/可导出的 trace API
- 未完成：B6 OpenCode 支持、B7 多 persona 知识工作流、B8 Workspace type 分类、B9 显式子目录规范继续留在 v1.2+ 或延后

## 6. B6–B9 决策结论

- B6 决策：OpenCode 保留为 v1.1 官方支持 runtime；v1.2 不新增官方深度适配、transport 补齐或 router 优先绑定。决策记录见 `docs/decisions/runtime-matrix.md`。
- B7 决策：v1.x 主线 persona 收敛为 independent developer；其他 persona 只保留为 skill/template 示例，不做独立用户系统或 broad media surface。决策记录见 `docs/decisions/v1.2-persona-workspace-boundary.md`。
- B8 决策：保留 `workspace_type`，默认继续为 `project`；v1.2 只实现 Project workspace，`personal` / `business` 先作为 enum 占位。决策记录见 `docs/decisions/v1.2-persona-workspace-boundary.md`。
- B9 决策：保留最小目录契约与 `context/` 子文件，允许 project assets 存在于 workspace 之外，不强制恢复原始 PRD 的全端子目录规范。决策记录见 `docs/decisions/v1.2-persona-workspace-boundary.md`。
