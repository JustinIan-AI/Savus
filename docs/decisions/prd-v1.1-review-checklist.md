# LoopDesk PRD v1.1 Review Checklist

> Status: Ready for review
> Owner: Product / Engineering
> Last updated: 2026-07-28
> Input: `docs/research/prd-gap-analysis-original-vs-v1.1.md:1`

## 1. 评审目标

本清单用于把原始 PRD 与当前 PRD v1.1 的差距，收敛成 **v1.1 可直接拍板的决定**。

每个条目只要求给出一个结论：
- **保留显式**：补进 v1.1，作为可验收的需求或术语定义
- **隐性承担**：不新增条目，由现有模块承担并补充说明
- **延后**：进入 v1.2 backlog，不改 v1.1
- **放弃**：明确不纳入后续主线，避免范围膨胀

## 2. 叙事与术语层

| # | 差距项 | 结论 | 需要补充的证据/文档 |
| --- | --- | --- | --- |
| N-1 | `Harness` 是否仍需作为团队沟通术语 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请在 `docs/prd/personal-loop-workspace-v1.1.zh.md` 或术语表补一行映射 |
| N-2 | `Intent Engine` 是否独立成节 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若隐性承担，请在 triage / context assembly 小节显式说明承担边界 |
| N-3 | `Task Planner` 是否独立成节 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若隐性承担，请说明 planner 责任由 Loop/Goal 还是 triage 承接 |
| N-4 | `Continuous Learning Loop` 是否作为产品能力名保留 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请给出最小定义，避免沦为 slogan |
| N-5 | 多 persona 是否进入 v1.x | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若不进入，请在 `docs/prd/personal-loop-workspace-v1.1.zh.md` 显式说明收窄原因 |

## 3. 模块与能力层

| # | 差距项 | 结论 | 需要补充的证据/文档 |
| --- | --- | --- | --- |
| M-1 | 显式 `context/` 子结构：`user.md`、`project.md`、`task_context.md` | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请在 Workspace State Protocol 定义最小 schema 或目录约定 |
| M-2 | 统一 `AgentRuntime` 抽象接口 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请明确是否仅作文档接口，还是进入实现面 |
| M-3 | 显式 ACP Gateway / discovery / context injection / state sync | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请补充到 `docs/prd/personal-loop-workspace-v1.1.zh.md` 或架构文档 |
| M-4 | 显式智能路由 / Router | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请说明路由输入、输出和人工可干预点 |
| M-5 | 显式智能意图识别 / intent classification | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请说明是产品能力还是实现细节 |
| M-6 | 显式任务拆解 Engine / DAG / task graph / agent assignment | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请说明最小 DAG 表达和是否允许并行执行 |
| M-7 | Execution Trace / Run Log schema | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请定义最小字段和消费者（Web/CLI/IM/replay） |

## 4. 数据模型与目录层

| # | 差距项 | 结论 | 需要补充的证据/文档 |
| --- | --- | --- | --- |
| D-1 | Workspace type 分类：Project / Personal / Business | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若不保留，请在 PRD 明确写“v1.x 只做 project workspace” |
| D-2 | Workspace 子目录规范：`context/`、`tasks/`、`memory/`、`skills/`、`tools/`、`agents/`、`logs/` | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请与 `.loopdesk/` + `LOOP-STATE.json` 的关系写清 |
| D-3 | Task JSON schema / execution trace schema | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请与 `LOOP-STATE.json` schema 对齐，避免双真源 |
| D-4 | Context 子模型：user / project / task | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请说明三类 context 的读写权限与 compact 策略 |

## 5. 运行时与 MVP 范围层

| # | 差距项 | 结论 | 需要补充的证据/文档 |
| --- | --- | --- | --- |
| R-1 | OpenCode 是否保留为 v1.x 支持 runtime | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保留，请在 adapter 能力表中补一行；若不保留，请写“不在官方支持矩阵” |
| R-2 | IM 全平台是否仍列为 v0.2 待排期 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若保持延后，请锁定 approved set：DingTalk、Feishu/Lark、Slack、WeCom |
| R-3 | 知识工作者 / 技术负责人 persona 是否进入 v1.1 或 v1.2 | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若不进入，请在用户章节显式说明当前主线 persona 边界 |
| R-4 | 通用知识工作流（信息收集 / 分析 / 写作 / 自动执行）是否进入 v1.x | ☐ 保留显式 / ☐ 隐性承担 / ☐ 延后 / ☐ 放弃 | 若不进入，请避免文档用“个人工作流”暗示通用知识工作覆盖 |

## 6. 评审结论记录

| 评审轮次 | 日期 | 参与者 | 结论摘要 |
| --- | --- | --- | --- |
| v1.1 review | 2026-07-28 | Product / Engineering | 已完成初步确认；Harness 仅保留为术语映射，不独立成节；Intent Engine / Task Planner / Continuous Learning Loop 均保留为独立能力节；多 persona 进入 v1.1；context/ 子结构保留；AgentRuntime 接口保留；ACP Gateway 保留；Router 保留；intent classification 保留；task graph/DAG/agent assignment 保留；Execution Trace schema 保留；Workspace type 保留并先只实现 Project；显式子目录规范保留；OpenCode 保留为 v1.1 官方支持 runtime；桌面分发采用本地 runtime + system launcher。 |
| v1.1 review follow-up | 2026-07-28 | Product / Engineering | 补录 v0.2/v1.1 附加结论：docs/channels.md 继续 minimal/internal 但补 operator docs；IM 扩大平台前先只开放 approved set，并以 allowlist + disable-by-default + audit log 为基线；loopdesk → loopdesk 全量迁移在 v1.0+ 立即启动。 |

## 7. 后续动作

1. 按本清单完成 v1.1 review，并把每条结论回填到 `docs/prd/personal-loop-workspace-v1.1.zh.md`。
2. 被判定为 **延后** 的条目，直接进入 `docs/plans/prd-v1.2-gap-backlog.md`。
3. 被判定为 **放弃** 的条目，应在 `docs/decisions/risk-handling-plan.md` 或 v1.1 中补充一句话边界说明。
