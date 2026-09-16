# LoopDesk 文档

本目录是面向用户的产品文档集，与根目录的发布 README 互补，提供任务导向的 LoopDesk 指南。

## 先读这些

1. [`quickstart.md`](quickstart.md) - 安装、配置、运行并打开 Web UI。
2. [`use-cases.md`](use-cases.md) - 面向常见目标的实用配方。
3. [`gateway.md`](gateway.md) - gateway 生命周期、host/port、安全与状态。
4. [`configuration.md`](configuration.md) - provider、router、search、channel、memory 与权限配置。
5. [`cli.md`](cli.md) - 命令分组与常用 CLI 工作流。
6. [`web-ui.md`](web-ui.md) - 本地控制台（Codex 三栏布局：任务看板、团队资产市场、设置）。
7. [`sessions.md`](sessions.md) - 会话连续性、导出、恢复、终止与清理。
8. [`glossary.md`](glossary.md) - 面向用户的术语表（中文为主，含循环工程术语）。

## 功能指南

- [`features.md`](features.md) - 能力目录。
- [`features/squilla-router.md`](features/squilla-router.md) - 模型路由。
- [`features/tool-compression.md`](features/tool-compression.md) - 工具结果压缩与句柄。
- [`prd/loopdesk-prd-v2.0.zh.md`](prd/loopdesk-prd-v2.0.zh.md) - **当前权威 PRD（v2.0 完整版）**：团队循环工作区、116 条能力清单、Codex 三栏前端清单。
- [`plans/loopdesk-webui-design-spec.md`](plans/loopdesk-webui-design-spec.md) - **WebUI 设计规格 v2.0**（Codex 三栏范式）。
- [`prd/personal-loop-workspace-v1.0.zh.md`](prd/personal-loop-workspace-v1.0.zh.md) - 历史：v1.0 PRD（Desktop-first runtime、Web surface、IM remote control）。
- [`prd/personal-loop-workspace.en.md`](prd/personal-loop-workspace.en.md) - 历史：v1.0 PRD 英文版。
- [`features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`](features/loopdesk-v0.2-channel-adapter-feature-breakdown.md) - 可选的 IM channel adapter 功能拆解。
- [`features/meta-skills.md`](features/meta-skills.md) - 可复用工作流技能。
- [`features/meta-skill-user-guide.md`](features/meta-skill-user-guide.md) - 面向用户的 MetaSkill 指南。
- [`authoring/meta-skills.md`](authoring/meta-skills.md) - MetaSkill 编写指南。
- [`features/memory.md`](features/memory.md) - durable memory 与召回。
- [`features/skills.md`](features/skills.md) - 技能的发现、安装与编写。
- [`features/compaction-and-cache.md`](features/compaction-and-cache.md) - 长会话压缩与 prompt-cache 连续性。
- [`prd/personal-loop-workspace-v1.1.zh.md`](prd/personal-loop-workspace-v1.1.zh.md) - 历史：v1.1 PRD（control-plane 侧重、handoff CLI、human model）。
- [`guides/guided-handoff.md`](guides/guided-handoff.md) - 首次 handoff 流程：项目、循环、worktree 与恢复。
- [`releases/loopdesk-v1.1.md`](releases/loopdesk-v1.1.md) - LoopDesk v1.1 发布说明。
- [`acceptance/loopdesk-v1.1-acceptance-checklist.md`](acceptance/loopdesk-v1.1-acceptance-checklist.md) - v1.1 发布验收清单。

## 用户面与运维

- [`releases/loopdesk-v0.2.md`](releases/loopdesk-v0.2.md) - LoopDesk v0.2 channel adapter 发布说明。
- [`releases/0.3.1.md`](releases/0.3.1.md) - LoopDesk 0.3.1 发布说明。
- [`releases/0.3.0.md`](releases/0.3.0.md) - LoopDesk 0.3.0 发布说明。
- [`channels.md`](channels.md) - 支持的消息渠道与配置流程。
- [`providers-and-models.md`](providers-and-models.md) - LLM provider 目录、模型选择与 runtime 模型检查。
- [`search.md`](search.md) - 网络搜索 provider 与查询工作流。
- [`artifacts-and-media.md`](artifacts-and-media.md) - 交付物、生成文件、图片、PDF 与 TTS。
- [`tools-and-sandbox.md`](tools-and-sandbox.md) - 内置工具、审批、沙箱姿态与写入策略。
- [`approvals-and-permissions.md`](approvals-and-permissions.md) - 权限配置、审批命令、工作区限制与沙箱姿态。
- [`agents.md`](agents.md) - durable 命名 agent 与工作区默认值。
- [`scheduling.md`](scheduling.md) - 周期性与一次性计划任务。
- [`mcp-server.md`](mcp-server.md) - 面向支持 MCP 客户端的 MCP server 桥接。
- [`usage-and-cost.md`](usage-and-cost.md) - token 用量、预估成本与成本排查工作流。
- [`diagnostics-and-replay.md`](diagnostics-and-replay.md) - 诊断、原始抓取指引与只读轮次重放。

## 调研与决策

- [`research/loop-engineering.md`](research/loop-engineering.md) - `loop-engineering` 调研结论及对 LoopDesk 的方法论借鉴。
- [`research/competitive-intel.md`](research/competitive-intel.md) - 竞品调研总览（Tutti/WeSight/Multica/Happier/cc-connect/Orca/Octos/Herdr/Proma 等）。
- [`research/competitive-intel-multica.md`](research/competitive-intel-multica.md) - `multica-ai/multica` 最新版专项调研（v0.4.43，2026-09-11）：人机团队、Squads、Skills、Autopilots、26 种 runtime。
- [`research/prd-optimization-suggestions.md`](research/prd-optimization-suggestions.md) - 基于调研与竞品分析的 PRD 优化建议（v1.1 → v1.2 输入）。
- [`research/competitive-intel-octos.md`](research/competitive-intel-octos.md) - `octos-org/octos` 竞品调研：本地 runtime、goals/loops、MCP/ACP、channels、swarm。
- [`research/octos-overview.md`](research/octos-overview.md) - `octos-org/.github` profile README 与 `octos-org/octos` 代码树调研摘要。
- [`decisions/desktop-web-im-product-boundary.md`](decisions/desktop-web-im-product-boundary.md) - LoopDesk Desktop-first / Web / IM 产品边界与 v1.0 方向决策。
- [`decisions/dsh-base-integration-proposal.md`](decisions/dsh-base-integration-proposal.md) - LoopDesk × DSH 集成提案：以 DSH 为 Agent Runtime 底座的工作台（可行性方向，含能力映射、四层架构、Python 集成路径）。
- [`decisions/full-package-rename.md`](decisions/full-package-rename.md) - 全量包名迁移决策。
- [`plans/2026-07-13-v02-channel-adapter-implementation-plan.md`](plans/2026-07-13-v02-channel-adapter-implementation-plan.md) - LoopDesk v0.2 IM channel adapter 可执行实施计划（钉钉、飞书、Slack、WeCom）。
- [`plans/2026-09-16-issue-fix-end-to-end-flow.zh.md`](plans/2026-09-16-issue-fix-end-to-end-flow.zh.md) - 对标 LoopX 的自动修复端到端操作流程（**两层架构**：任务控制面 / 能力供给面 + 九步处置 + **字段驱动总表** + 原型映射），**细化画布与 WebUI 原型的流程依据**。
- [`operations.md`](operations.md) - 会话、cron、用量、诊断、迁移、MCP server 与安装清单命令。
- [`plans/2026-07-07-loopdesk-implementation-plan.md`](plans/2026-07-07-loopdesk-implementation-plan.md) - LoopDesk v0.1 实施计划，包含 FDD、TDD 与 Loop Engineering 执行边界。
- [`troubleshooting.md`](troubleshooting.md) - 常见安装/运行时问题。
- [`glossary.md`](glossary.md) - 术语表（**中文为主**）：LoopDesk 产品概念 + **循环治理术语** + 遗留词映射。

## 改进文档

欢迎改进文档。先读 [`contributing-docs.md`](contributing-docs.md) 获取文档相关指引，再向 `dev` 分支提交一个小而聚焦的 pull request。

快捷路径：

- 报告过时命令、失效链接或令人困惑的页面：使用 [文档问题模板](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)。
- 直接在 GitHub 上编辑对应的 Markdown 页面，并向 `dev` 分支提交聚焦的 pull request。
- 新增功能文档时，独立功能放在 `docs/features/` 下的独立页面。

## 设计原则

LoopDesk 文档应优先帮助用户把产品跑起来，其次才是理解它的独特优势。机制繁重的 runtime 细节应放在开发者设计说明或源码注释里，而不是首跑路径中。

---

[产品指南](../README.product.md) · [改进这些文档](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml) · [贡献指南](../CONTRIBUTING.md)
