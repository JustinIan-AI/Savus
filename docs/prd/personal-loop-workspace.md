# PRD — LoopDesk 团队循环工作区（Team Loop Workspace）

> ⚠️ 本文为 v0.2 团队视角 PRD，已并入并扩展为完整版 **[`loopdesk-prd-v2.0.zh.md`](./loopdesk-prd-v2.0.zh.md)**（含全部竞品调研借鉴与 116 条功能清单）。**v2.0 为当前权威 PRD**，本文保留为 v0.2 阶段记录。

> Status: Draft（重构版）
> Version: v0.2（团队开发视角，承接 v0.1 个人循环工作区）
> Owner: Product / Engineering
> Last updated: 2026-09-11
> Sources: docs/architecture/personal-loop-workspace.md(v0.2)、docs/research/competitive-intel-loopx.md、competitive-intel-tutti-os-tutti.md、competitive-intel-proma.md、docs/decisions/*

## 0. 定位转变说明（Why v0.2）

v0.1 面向独立开发者（personal），并显式把"团队协同 / 云房间 / 团队治理"列为 Non-Goals。但最新竞争态势已改变：

- **Tutti**（`tutti-os/tutti`，3.7k★）以"多用户多代理实时共享工作区 + Big @ 跨代理引用 + 代理借用 + 房间隔离"正面占领"团队能力复用"心智。
- **LoopX**（`huangruiteng/loopx`，2.5k★）以"长程 agent 控制平面 + peer agent teams + quota/gate + typed handoff + 200h 真实运行"正面占领"长任务自动完成与治理"心智。
- **Proma**（`proma-ai/proma`）企业版已产品化"团队额度管理 + Skills 组织级分发 + Cloud API Key 额度"。

三者均与 LoopDesk 直面冲突。因此 v0.2 将产品重心从"个人"升级为**团队开发**，但坚持 LoopDesk 的 local-first 编排内核与差异化（可移植跨工具状态、adapter-first、loop 工程护栏）。本 PRD 直接承接用户给出的 5 条团队约束。

> 一句话定位：**LoopDesk 是一个 local-first 的团队循环工作区**——在开发者自有机器上统一编排 claude、codex、pi 等 agent 完成任务，并通过跨 agent / 跨会话 / 跨团队的上下文传递，以及团队 AI 资产（Specs / Rules / Skills / MCP / 交付物）的 git 化分发，让团队像拥有"项目管理部"一样持续运转长任务。

---

## 1. Purpose（目的）

定义 LoopDesk 作为**团队循环工作区**的需求：在 local-first 前提下，帮助研发团队在 claude、codex、pi 等多 agent、多会话、多工具之间保持任务上下文连贯，复用团队 AI 资产，并以 LoopX 式长任务模板安全、可控地完成 issue-fix、pr-commit、auto-research 等真实研发场景。

## 2. Background（背景）

研发团队的真实工作流天然分散：任务在 JIRA / Plane，知识在 Confluence，编码分散在 claude / codex / pi 等多个 agent。每个 agent 有独立会话与上下文，人成为手动桥接层——重复解释需求、搬运上下文、重建决策。

我们需要一个 local-first 的团队层：把任务系统与知识库接入工作区，让多个 agent 在统一调度下协作完成任务，且团队沉淀的 Specs / Rules / Skills / MCP / 交付物能通过 git 仓库在成员间复用与下发，长任务能像 LoopX 那样自动跑完并留下可审计证据。

## 3. Goals and Non-Goals

### Goals（目标，对应 5 条约束）
1. **MCP 与系统集成**：默认可从 JIRA、Plane 等任务管理系统同步任务，从 Confluence 等知识库获取项目相关知识。（约束 1）
2. **local-first agent 编排**：核心在于 local-first 调度 claude、codex、pi 等 agents 完成任务。（约束 2）
3. **跨 agent / 跨会话 / 跨团队上下文传递**：任务上下文支持在 agent 之间、会话之间、团队之间传递。（约束 3）
4. **团队 AI 资产管理**：包含但不限于 Specs、Rules、Skills、MCP、交付物，通过 GitHub 等代码仓库共享；其中 Rules、Specs、Skills 支持下发。（约束 4）
5. **长任务自动完成与模板**：支持 LoopX 类似方案的长任务自动完成；参考 LoopX showcases 提供 issue-fix、pr-commit、auto-research 等场景，并形成固定模板在 LoopDesk 中便于用户使用。（约束 5）

### Non-Goals（非目标）
- 不做 Tutti 式强实时云房间 / 多人同时编辑；保留 local-first，共享/房间为可选能力。
- 不取代 claude、codex、pi 等 agent runtime；LoopDesk 是控制/编排层。
- 不做重桌面 GUI；坚持 CLI + 本地 Web UI 的轻量形态。
- 不强制中心化多租户 SaaS；团队共享以 git 仓库为底座，云仅作可选同步。
- 不把"团队额度商业化 / SaaS 计费"作为 v0.2 核心（参照 Proma 企业版方向，仅预留接口）。

## 4. Target Users（目标用户，团队视角）

Primary：小型研发团队、技术负责人、以及在团队中工作的独立开发者。
Needs：
- 从 JIRA/Plane + Confluence 拉取任务与知识，无需手动搬运到 agent。
- 让 claude/codex/pi 等 agent 在统一调度下协作，避免冲突与重复。
- 跨 agent / 跨会话 / 跨团队保持上下文连贯与可交接。
- 复用团队沉淀的 Specs/Rules/Skills/MCP，并能一键下发给成员。
- 用 issue-fix / pr-commit / auto-research 等模板安全跑完长任务，可审计、可重启。

## 5. User Experience & Core Scenarios（核心场景）

### Scenario A — 任务与知识接入（约束 1）
- 团队连接 JIRA / Plane：LoopDesk 通过 MCP 连接器拉取 issue/任务到工作区，并把进度/结果/链接回写任务系统。
- 团队连接 Confluence：MCP 连接器把相关页面/空间索引为项目知识库，agent 执行时可「+引用」直接消费，无需复制全文。
- 默认连接器：JIRA、Plane、Confluence；连接器以 MCP Server 形式可插拔扩展。

### Scenario B — local-first 编排 agent 完成任务（约束 2）
- 从任务/知识生成 Goal；LoopDesk 在本地选择并调度 claude / codex / pi 等注册 agent。
- 每个 agent 在隔离 worktree/scratch 中执行，带预算、权限、stop condition。
- 控制中心统一展示所有 agent 会话、待审批操作、运行任务。

### Scenario C — 跨 agent / 跨会话 / 跨团队上下文传递（约束 3）
- 任务上下文（目标、决策、证据、待办、交接）以团队级 Workspace State 持久化。
- 一个 agent 完成的部分工作，下一 agent（可能是不同工具、不同会话、不同成员）通过 handoff packet 直接续跑，无需人重复解释。
- 支持跨团队：团队 A 的某 Spec/Rule/交付物可经 git 仓库作为上下文传入团队 B 的工作区。

### Scenario D — 团队 AI 资产下发（约束 4）
- 团队 AI 资产注册表收录 Specs、Rules、Skills、MCP 配置、交付物，统一存于 GitHub 等代码仓库。
- Rules、Specs、Skills 支持"下发（distribute/push）"：管理员/owner 一键将资产推送到成员工作区，免安装、版本统一。
- 资产可版本化、可审计、可回滚；MCP 配置与交付物随仓库共享但不强制下发。

### Scenario E — 长任务模板自动完成（约束 5，LoopX 式）
- 内置长任务模板：**issue-fix**（滚动仓库上下文 + 带版本修复知识）、**pr-commit**（生成/打磨 PR 与提交）、**auto-research**（proposer→executor→evaluator 多角色迭代）。
- 长任务受 quota/gate 治理：health → operator → evidence → focus → compute quota 决策链，关键关口需人审批。
- 模板形成固定骨架，用户在 LoopDesk 中可直接选用并填参，无需从零搭建。

## 6. Scope（范围）

### 6.1 In Scope for v0.2（团队）
- **MCP Adapter + 默认连接器**：JIRA、Plane（任务同步）、Confluence（知识获取），双向同步 + 可插拔。
- **Agent Orchestrator**：claude / codex / pi 等 agent 注册、调度、worktree 隔离、预算与权限。
- **团队级 Workspace State**：跨 agent / 跨会话 / 跨团队上下文与 handoff packet。
- **团队 AI 资产注册表**：Spec / Rule / Skill / MCP / Deliverable；git 仓库共享；Rules/Specs/Skills 下发与版本管理。
- **长任务模板引擎**：issue-fix / pr-commit / auto-research；LoopX 式 quota/gate 治理与 run log。
- 沿用 v0.1：Loop Engine（triage / maker-checker / stop condition）、Memory、Skills、Worktree 隔离、成本/审批护栏、CLI + 本地 Web UI。

### 6.2 Out of Scope for v0.2
- 强实时云房间、多人同时编辑、IM-first 产品形态。
- 重桌面 GUI / Electron 壳。
- 中心化多租户 SaaS 与团队额度商业化计费（仅预留接口，参照 Proma 企业版）。
- 完全替代成熟 issue board / 知识库（LoopDesk 通过 MCP 连接，而非重建）。

## 7. Requirements（需求，逐条对应约束）

### 7.1 MCP 与系统集成（约束 1）
- 系统 MUST 以 MCP-first 集成外部系统；MCP 连接器对工具、资源、prompt、事件统一建模。
- 系统 MUST 提供默认任务连接器：JIRA、Plane，支持拉取任务/issue 进入工作区，并把进度、结果、关联链接回写。
- 系统 MUST 提供默认知识库连接器：Confluence，支持索引/检索页面空间为项目知识，agent 可引用消费。
- 系统 SHOULD 允许连接器以 MCP Server 形式插拔扩展（除 JIRA/Plane/Confluence 外可加 GitHub、Linear、Notion 等）。
- 系统 MUST 将 inbound 任务/知识事件翻译为 Workspace State，并将工作区产出翻译回任务/知识系统。

### 7.2 Agent 编排（约束 2）
- 系统 MUST 在 local-first 前提下注册并调度多个 agent（claude、codex、pi 等），不取代其 runtime。
- 系统 MUST 维护 agent 注册表（provider、runtime、指令、env、MCP 配置、Skills、最大并发）。
- 系统 MUST 支持按任务类型/成本/历史结果选择 agent；调度保留 human override，不允许无界自动路由。
- 系统 MUST 在隔离 worktree/scratch 中执行 agent 任务，带审批、预算上限与 stop condition。
- 系统 MUST 暴露控制中心统一视图：所有 agent 会话、待审批操作、运行任务。

### 7.3 跨 agent / 跨会话 / 跨团队上下文传递（约束 3）
- 系统 MUST 以团队级 Workspace State 持久化任务上下文（目标、决策、证据、待办、交接、配额）。
- 系统 MUST 支持 handoff packet：一个 agent/会话/成员完成的上下文可被下一执行方直接消费续跑。
- 系统 MUST 支持跨会话连续性（resume / history / replay / export / abort）。
- 系统 SHOULD 支持跨团队上下文引用：经 git 仓库共享的资产（Spec/Rule/Deliverable）可作为另一团队工作区的上下文输入。
- 系统 MUST 保证上下文传递不依赖复制粘贴，且跨工具可移植、可审计。

### 7.4 团队 AI 资产管理（约束 4）
- 系统 MUST 建立团队 AI 资产注册表，资产类型至少含：Spec、Rule、Skill、MCP 配置、Deliverable（交付物）。
- 系统 MUST 支持资产经 GitHub 等代码仓库共享（clone / pull / push），资产即仓库内可版本化文件。
- 系统 MUST 支持 Rules、Specs、Skills 的"下发（distribute/push）"：由 owner/管理员推送到成员工作区，免安装、统一版本、可回滚。
- 系统 SHOULD 对资产做版本管理、审计与使用范围控制；MCP 配置与交付物随仓库共享但不强制下发。
- 系统 SHOULD 支持资产的发现/检索/复用（类似 Skills Hub / 应用中心，但 local-first）。

### 7.5 长任务自动完成与模板（约束 5，LoopX 式）
- 系统 MUST 提供长任务模板引擎，内置至少 **issue-fix / pr-commit / auto-research** 三类固定模板。
- 系统 MUST 让模板可参数化选用（用户在 LoopDesk 中选模板 → 填参 → 运行），形成固定骨架降低搭建成本。
- 系统 MUST 对长任务实施 LoopX 式治理：quota 决策（`should-run`）、五级 gate（health→operator→evidence→focus→quota）、typed turn 结果枚举、typed handoff。
- 系统 MUST 为长任务记录 run log（证据、验证状态、阻塞项、已接受 writeback），可审计、可重启、可交接。
- 系统 SHOULD 沉淀"带版本修复知识 / 决策谱系 / reward 信号"，提升后续同类任务质量（参考 LoopX evidence / reward memory / decision context）。

### 7.6 安全 / 成本 / 治理（沿用 v0.1 并增强）
- 系统 MUST 跟踪 token 与成本，执行预算上限、日限、最大迭代、kill switch。
- 系统 MUST 提供审批队列（敏感动作、生产操作、发布需人审批——参照 LoopX operator gate）。
- 系统 MUST 支持升级（ambiguity / 重复失败 / denylist 路径）与公私边界（不提交凭证、私有日志、活跃 goal 状态）。
- 系统 MUST 支持 per-loop worktree 隔离与审计快照，避免跨任务工作区污染。

## 8. Success Metrics（成功指标）
- 任务接入成本：从 JIRA/Plane + Confluence 到 agent 可消费的准备时间下降。
- 上下文传递保真度：跨 agent / 跨会话 / 跨团队交接中保留任务状态、决策、资产的比例。
- 资产复用率：Rules/Specs/Skills 下发后被成员实际复用的比例。
- 长任务完成率：issue-fix / pr-commit / auto-research 模板达到 stop condition 的比例。
- 成本可预测性：在预算与 gate 阈值内的 loop 运行占比。

## 9. Launch Criteria（发布标准）
- MCP 默认连接器（JIRA/Plane/Confluence）可成功双向同步。
- Agent Orchestrator 可注册并调度 claude/codex/pi 至少两类 agent 完成一个 Goal。
- 团队级 Workspace State 支持跨会话 handoff 且可审计。
- 团队 AI 资产注册表可经 git 仓库共享，Rules/Specs/Skills 可一键下发到成员工作区。
- issue-fix / pr-commit / auto-research 模板可在 quota/gate 治理下跑通至少一个真实任务并留 run log。

## 10. Risks and Mitigations（风险与缓解）

| Risk | Mitigation |
| --- | --- |
| 与 Tutti/LoopX 正面竞争，差异化不足 | 坚持 local-first 编排 + git 化资产分发 + 长任务模板，不做强实时云房间 |
| MCP 连接器覆盖不全 | 优先 JIRA/Plane/Confluence，连接器以 MCP Server 插拔扩展 |
| 跨团队上下文引发隐私/权限问题 | 显式公私边界 + 资产下发范围控制 + 房间级隔离 |
| 长任务自动完成失控 | LoopX 式 quota/gate + 关键关口人审批 + kill switch |
| 团队资产下发造成版本漂移 | 资产 git 版本化 + 下发版本锁定 + 可回滚 |

## 11. Open Questions（开放问题）
- v0.2 是否需要"实时房间"作为可选形态，还是严格 local-first + git 异步共享？
- 团队资产下发与 Proma 企业版 Skills 分发在边界上如何差异化（git 原生 vs Cloud 托管）？
- LoopX 的 peer agent teams（claim/lease）是否需要在 v0.2 引入，还是先以"多人各带 agent + 工作区共享"简化？
- 长任务模板是否开放为可自定义模板市场（参照 Tutti 应用生态）？

## 12. Approval（审批）

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
