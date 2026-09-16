# 产品定位

> 目标用户：小型研发团队 / 技术负责人 / 在团队中工作的开发者，使用 claude、codex、pi 等多 agent 与 JIRA/Plane/Confluence 等系统。
> 竞品锚点：`tutti-os/tutti`、`huangruiteng/loopx`、`proma-ai/proma`、`freestylefly/wesight`、`multica-ai/multica`、`octos-org/octos`。
> 决策原则：在团队开发场景下竞争——以 local-first 编排 + 跨工具上下文 + 团队 AI 资产 git 分发 + LoopX 式长任务模板制胜；不与 Tutti 抢强实时云房间、不与 LoopX 抢纯控制平面内核、不与 Proma 抢 Cloud 托管分发。
> 关联：PRD `docs/prd/personal-loop-workspace.md`（v0.2 团队循环工作区）、架构 `docs/architecture/personal-loop-workspace.md`（v0.2）。

## 核心定位

**一个 local-first 的团队循环工作区**：编排 claude、codex、pi 等 agent 完成真实的研发任务——具备跨 agent / 跨会话 / 跨团队上下文交接、git 支持的团队 AI 资产分发，以及 LoopX 式长任务模板（issue-fix / pr-commit / auto-research）。

这不是又一个 AI IDE，也不是又一个终端 agent 包装器。它是团队的操作层：让每个工具的上下文保持连贯、决定下一步该跑什么、把可复用的 Specs/Rules/Skills 在团队内分发，并阻止人沦为 agent 与任务之间的手动桥梁。

## 竞争定位

| 竞品 | 擅长 | 过度交付 | LoopDesk 的差异化 |
| --- | --- | --- | --- |
| `tutti-os/tutti` | 共享 agent 工作区、Big @ 跨代理引用、代理借用、房间隔离 | 实时云房间、多人同时编辑、广泛的创作者用例 | local-first + git 异步资产共享，不强制强实时云房间；团队 AI 资产 git 原生分发 |
| `huangruiteng/loopx` | 长程控制平面、peer agent teams、quota/gate、typed handoff、200h 实证 | 纯控制平面内核、供应商中立治理 | 直接引入其 quota/gate/typed-handoff 与 issue-fix/auto-research 模板，并叠加 JIRA/Plane/Confluence 接入与团队资产分发 |
| `proma-ai/proma` | 本地优先桌面 Chat/Agent 工作台、Skills/MCP、企业版 Skills 分发、Cloud API Key | 桌面壳优先、Cloud 托管的模型渠道与额度 | git 原生资产分发 + 本地编排，避免绑定 Cloud 计费 |
| `freestylefly/wesight` | 桌面可见性、多引擎统一、运行时指标 | GUI 壳广度、IM 集成 | 轻量上下文/循环层，而非 GUI 包装器 |
| `multica-ai/multica` | issue 驱动的 agent 工作、autopilot、会话恢复 | 团队治理、成员角色、实时化 | 聚焦团队资产/上下文，不带沉重的 issue 看板/角色复杂度 |
| `octos-org/octos` | 多面 agent runtime、goals/loops、MCP/ACP、skills registry | 多租户/云广度、重壳 | 精简的 local-first 可移植循环交接 |

## 战略差异点

- **上下文连续性，升级到团队规模**：workspace state 即产品；跨 agent / 跨会话 / 跨团队交接，而非复制粘贴。
- **工具中立的循环 + 编排**：MCP-first 集成；Agent Orchestrator 在本地调度 claude/codex/pi，不取代它们的 runtime。
- **Loop engineering 纪律**：L1 报告 → L2 辅助 → L3 无人值守，外加 LoopX 式 quota/gate 与 maker/checker 分离。
- **本地控制 + git 支持的团队资产**：local-first runtime；Specs/Rules/Skills/MCP/交付物经 GitHub 仓库共享，支持一键下发/推送与版本管理。
- **开箱即用的长任务模板**：issue-fix / pr-commit / auto-research 作为固定、可参数化的模板，参考 LoopX showcases。
- **最小可用使用面**：CLI + 本地 Web UI（控制中心）；避免过度的重桌面应用或 IM-first 复杂度。

## 产品承诺

- 把 JIRA/Plane 任务与 Confluence 知识接入同一工作区；agent 无需手动搬运即可消费。
- 在 claude 中启动任务；在 codex 或 pi 中继续，无需重新粘贴上下文、项目规则或决策。
- 看到当前 loop/goal 状态与团队资产状态，而不只是最新一条对话消息。
- 通过 git 一键把团队 Specs/Rules/Skills 下发给成员；可复用、可版本化、可审计。
- 以模板运行 issue-fix / pr-commit / auto-research，受 quota/gate 治理——可审计、可恢复、可交接。

## 定位声明

对于在 claude、codex、pi 以及 JIRA、Plane、Confluence 等工具之间切换的小型工程团队，LoopDesk 是一个 local-first 的团队循环工作区，跨 agent 与队友统一上下文、记忆、会话状态与循环控制。与 Tutti 不同，它保持 local-first，以 git 支持的异步共享替代强制实时云房间。与 LoopX 不同，它把控制平面治理与真实研发团队集成（JIRA/Plane/Confluence）及 git 原生资产分发配套。与 Proma 不同，它不把团队绑定到 Cloud 托管的模型/额度渠道。它为团队提供一个持久、可移植、可审计的循环层，让每个 AI agent 都能完成自己的工作，而无需人反复解释。
