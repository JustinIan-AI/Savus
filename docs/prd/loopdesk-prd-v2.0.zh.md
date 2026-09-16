# PRD — LoopDesk 团队循环工作区（完整版）

> 状态：v2.0 完整稿（评审中）
> 版本：v2.0（合并 v0.1 个人循环工作区 + v0.2 团队 + 全部竞品调研借鉴）
> 负责人：Product / Engineering
> 最后更新：2026-09-11
> 输入：`docs/prd/personal-loop-workspace.md`(v0.2)、`docs/prd/personal-loop-workspace-v1.1.zh.md`(v1.1)、`docs/architecture/personal-loop-workspace.md`、`docs/research/competitive-intel*.md`（25 份竞品调研）、`docs/research/loop-engineering.md`、`docs/research/octos-actionable-features.md`、`docs/research/proma-inspiration.md`、`docs/research/prd-optimization-suggestions.md`、`docs/research/prd-gap-analysis-original-vs-v1.1.md`、`docs/features/core-feature-list.md`

> **版本史**
> | 版本 | 日期 | 主要变化 | 权威状态 |
> | --- | --- | --- | --- |
> | v0.1 | 2026-07 | 个人循环工作区、local-first、CLI + 本地 Web、MCP-first | 历史参考 |
> | v1.0/v1.1 | 2026-07 | Control Plane、handoff、Human Model、P0 优化并入 | 历史参考（关键决策已继承） |
> | v0.2 | 2026-09-11 | 升级为团队循环工作区：MCP 系统集成、agent 编排、跨团队上下文、git 化 AI 资产、LoopX 式长任务 | 已继承 |
> | **v2.0** | **2026-09-11** | **合并全部调研借鉴，输出"功能最完整"PRD + 显式功能清单（§9）** | **当前权威 PRD** |

> **完成度图例**
> - ✅ = 已实现
> - 🔶 = 已实现 / 待验收
> - ⏳ = v0.2 范围（已决策，实现待排期）
> - 🔲 = 已设计 / 已决策，实现待排期
> - 🆕 = 本次完整版新增（来自调研借鉴，设计待排期）
>
> **优先级**：P0 = v2.0 必须；P1 = v2.0 应有；P2 = 后续增强

---

## 1. 一句话定位

**LoopDesk 是一个 local-first 的团队循环工作区**——在开发者自有机器上统一编排 claude、codex、pi 等 agent 完成任务，通过跨 agent / 跨会话 / 跨团队的上下文传递，以及团队 AI 资产（Specs / Rules / Skills / MCP / 交付物）的 git 化分发，让团队像拥有一个"项目管理部"一样持续、可审计、可控地完成长任务。

> **Elevator Pitch**：在任意支持的 agent 中启动任务，不用复制粘贴完整上下文，即可在另一个 agent / 会话 / 成员处续跑；看到的是当前 loop state 与团队资产，而不是最新一条 chat message。
>
> **30 秒 Demo**：安装 `loopdesk` → `loopdesk onboard` → 连 JIRA/Confluence → 选 `issue-fix` 模板 → LoopDesk 调度 claude 在隔离 worktree 修复 → quota/gate 把关 → 回写 JIRA + 留 run log → 换 codex 或另一位成员直接续跑。

---

## 2. 背景与竞争态势

### 2.1 问题

研发团队的真实工作流天然分散：任务在 JIRA / Plane，知识在 Confluence，编码分散在 claude / codex / pi 等多个 agent。每个 agent 有独立会话与上下文，人成为手动桥接层——重复解释需求、搬运上下文、重建决策。团队沉淀的 Specs / Rules / Skills / MCP / 交付物也散落在个人机器里，无法复用与治理。

### 2.2 竞品格局（详见 `docs/research/competitive-intel*.md`）

| 竞品 | 核心隐喻 | 对 LoopDesk 的价值 | 冲突 / 不借鉴 |
| --- | --- | --- | --- |
| `huangruiteng/loopx` | 长程 agent 本地控制平面 | quota/gate、typed turn、typed handoff、peer agent teams、evidence/reward memory | 不做 peer claim 取代 maker/checker；保持工作区效率重心 |
| `tutti-os/tutti` | 多用户多代理实时协作空间 | Big @ 跨代理引用、代理借用、房间隔离、人机共用应用中心 | 不做强实时云房间、不绑云运行时 |
| `proma-ai/proma`（企业版） | 本地优先桌面 Agent 工作台 | Skills 组织级分发、团队额度池、项目级 memory | 不做桌面 Chat shell；分发以 git 原生而非 Cloud 托管 |
| `octos-org/octos` | Agentic OS 后端 | `/goal` `/loop`、checkpoint/time-travel、MCP/ACP 一等、swarm ledger | 不做多租户/云托管/OS 宽度 |
| `mindfold-ai/trellis` | 项目层 agent harness | 真源+派生生成、工作流状态机+回归守护、作用域 spec 注入、ablate/restore | 不生成 22 平台文件；不改走 AGPL 源码；用运行时协议替代 |
| `Tencent/teamai-cli` | 团队级 AI 资产分发 | Git 即分发通道 + SessionStart 自动 pull、roles/tags/sources、代码图+BM25、friction 沉淀 | 不引入 Git 托管+MR 复杂度作为个人核心 |
| `AMAP-ML/LongHorizon-Harness` | CUA 长程 loop 框架 | Manager/Executor/Auditor 三角色、主动丢弃 execution history、文件哈希快照、审计控制头 | 不做 GUI 托管与顶层调度引擎 |
| `OpenBMB/PilotDeck` | WorkSpace 中心 agent OS | WorkSpace 隔离、白盒可编辑记忆、smart routing | 不做重型多面 agent OS |
| `bytedance/deer-flow` | LangGraph super-agent harness | `/goal`+evaluator+auto continuation+no-progress breaker、skill 包+allowed-tools、compact、scheduled task、observability contract | 不复制平台化叙事与重服务拓扑 |
| `generalaction/emdash` | 并行 agentic dev environment | worktree-per-task UX、issue 驱动、复用 library、tmux 长会话 | 不做重桌面外壳 |
| `crynta/terax-ai` | 轻量 terminal-first ADE | 五层安全语法、live context bridge、approval-as-boundary、meta-orchestration | 不做 all-in-one app；连续性保持 portable |
| `herdrdev/herdr` | terminal-native agent multiplexer | 真实 PTY 保留、blocked/working/done rollup、native resume、live handoff、plugin/socket API | 不做单 runtime-server-first 心智 |
| `block/buzz` | 团队 hive mind | agent personas/teams、ACP/MCP 协议边界、hash-chain 审计、上下文溢出摘要 | 不做 Nostr 社交平台/重基础设施 |
| `Zleap-Agent` | workspace 隔离 agent runtime | 三层记忆（person/event/experience）、Memory Dream、skill trust/risk 元数据 | 不加 DB 依赖；不做 IM gateway/团队特性 |
| `stablyai/orca` / `yasinkavakli/orca` | 并行 worktree agent IDE | worktree + 赢家选择、annotate diff、headless/远程 host authority、用量可观测 | 不做 Electron IDE 外壳/品牌化 app |
| `ruvnet/ruflo` | agent meta-harness | GOAP 目标分解+plan tree、MCP 工具规模、自学习记忆 | 不做 swarm-first/插件市场主面 |
| `makecindy/cindy` | 多 harness workbench | 零摩擦 onboarding、harness 抽象+任务中切换、结构化 plugin 契约 | 不做云后端/遥测默认 |
| Raft Docs | 人机协作工作区文档面 | onboarding-as-narrative、task handoff、文档机器可读（`/llms.txt`） | 不做 room-first/team-first 核心 |
| `DeepSeek Harness`（dsh） | 可组合 Agent runtime | Profile/Bundle/Patch 热插拔、事件溯源会话日志、hooks 桥接 | 作为候选 runtime driver，保持 LOOP-STATE 独立 |
| 其余（WeSight / Multica / Happier / cc-connect / Bisheng / GOAI） | — | runtime 可见性、channel 宽度、企业治理纪律、validation receipt | 参见 §4.2「明确不采纳」 |

### 2.3 差异化空白（已验证）

**所有竞品的连续性都封在自家生态内**（Orca 在 worktree、Cindy 在 app、Octos 在自己 runtime、Herdr 在自己终端、Proma 在自己工作台、Trellis 在自己文件树）。没有一家提供**跨外部工具（Claude Code ↔ Codex ↔ Trae ↔ Gemini）可导入/导出的 durable loop state**。这正是 LoopDesk 的护城河：

1. 可移植的 durable `LOOP-STATE.json`（可机读、跨工具、可 diff/export）；
2. 显式 Loop Engineering 方法论（triage → maker → checker → escalation → run log → stop condition）+ 长任务模板；
3. 零基础设施 local-first（无服务器、无 DB、无云账号即可跑）；
4. git 原生的团队 AI 资产分发（差异化于 Proma 的 Cloud 托管分发）。

---

## 3. 目标与非目标

### 3.1 目标（对应 5 条团队约束）

1. **MCP 与系统集成**：默认可从 JIRA、Plane 等任务管理系统同步任务，从 Confluence 等知识库获取项目知识。（约束 1）
2. **local-first agent 编排**：核心在于 local-first 调度 claude、codex、pi 等 agents 完成任务。（约束 2）
3. **跨 agent / 跨会话 / 跨团队上下文传递**：任务上下文支持在 agent 之间、会话之间、团队之间传递。（约束 3）
4. **团队 AI 资产管理**：包含但不限于 Specs、Rules、Skills、MCP、交付物，通过 GitHub 等代码仓库共享；其中 Rules、Specs、Skills 支持下发。（约束 4）
5. **长任务自动完成与模板**：支持 LoopX 类似方案的长任务自动完成；参考 LoopX showcases 提供 issue-fix、pr-commit、auto-research 等场景，并形成固定模板在 LoopDesk 中便于用户使用。（约束 5）

补充目标：
- 把 `LOOP-STATE.json` 提升为 **Agent Working Memory Standard** 级资产（可移植、可机读、跨工具）。
- 让 Skill 从"Prompt 模板库"演进为 **Skill Engineering**（trigger / context / workflow / evaluation / feedback）。
- 引入轻量 Human Model 与团队级资产治理，但**坚持 local-first 与 adapter-first**。

### 3.2 非目标

- 不做强实时云房间 / 多人同时编辑（保留 local-first，共享/房间为可选）。
- 不取代 claude、codex、pi 等 agent runtime；LoopDesk 是控制/编排层。
- 不做重桌面 GUI / Electron IDE 壳。
- 不强制中心化多租户 SaaS；团队共享以 git 仓库为底座，云仅作可选同步。
- 不把"团队额度商业化 / SaaS 计费"作为 v2.0 核心（参照 Proma 企业版，仅预留接口）。

### 3.3 明确不采纳清单（范围护栏）

| 不采纳 | 来源竞品 | 理由 |
| --- | --- | --- |
| 强实时云房间 / 房间运行时 | Tutti | 违背 local-first；改用 git 异步资产 |
| peer claim 取代 maker/checker | LoopX | 保留显式独立验证语义 |
| 重多面 agent OS / 多租户 | Octos、PilotDeck | 范围膨胀，与个人/小团队定位冲突 |
| 22 平台配置文件生成 | Trellis | 用运行时协议（MCP/ACP）替代生成式适配 |
| all-in-one 桌面 ADE（终端+编辑器+Git+预览） | Terax、emdash、Orca | 连续性应 portable，不做重壳 |
| Nostr 社交平台 / hash 社交协议 | Block/Buzz | 需重基础设施，非协作层 |
| swarm-first 自动编排 / 大插件市场 | ruflo | 不做默认多 agent 主权 |
| 云后端 / 遥测默认 / 移动优先 | Cindy、Happier | 违背 local-first 与无账号默认 |
| 企业 LLMOps 重栈（ES/Milvus/OnlyOffice） | Bisheng | 与 LoopDesk 定位冲突 |
| 单 app 会话模型（埋没跨工具 handoff） | emdash | 与跨工具连续性核心冲突 |
| 文档/产品同名 "LoopDesk" 的企业编排方案 | GOAI（competition） | 品牌混淆；LoopDesk 为 local-first 控制平面，与任何企业多 Agent 编排方案无关 |

---

## 4. 目标用户

- **Primary**：小型研发团队、技术负责人，以及在团队中工作的独立开发者。
- **Needs**：
  - 从 JIRA/Plane + Confluence 拉取任务与知识，无需手动搬运到 agent。
  - 让 claude/codex/pi 等 agent 在统一调度下协作，避免冲突与重复。
  - 跨 agent / 跨会话 / 跨团队保持上下文连贯与可交接。
  - 复用团队沉淀的 Specs/Rules/Skills/MCP，并能一键下发给成员。
  - 用 issue-fix / pr-commit / auto-research 等模板安全跑完长任务，可审计、可重启。
- **Secondary**：Operator-developer（在另一设备/IM 查看状态、approve/reject）；Power user（对已批准 bounded 工作做跨设备继续）。

---

## 5. 产品叙事与差异化

### 5.1 产品承诺

- 在任意支持的 agent 中启动任务；
- 不复制粘贴完整上下文，即可在另一 agent / 会话 / 成员处继续；
- 看到当前 loop state 与团队资产，而不是最新一条 chat message；
- 让 LoopDesk 建议下一个 safe action、展示 cost，并记录 outcome；
- 把 decisions、artifacts、run history 保存在可搜索、可 diff 的团队工作区。

### 5.2 战略差异点

- **Local-first runtime**：安装、gateway、文件访问、agent 编排、inspection 都以本地为主。
- **Web 为辅**：分发、setup、inspection、approval、diagnostics。
- **IM 为 continuation surface**：选工作区、看状态、approve/reject、继续已批准 bounded work。
- **Context continuity first**：workspace state 是产品，不是 shell。
- **Tool-agnostic loop**：MCP-first、ACP-second、不强制 vendor UI。
- **Loop engineering discipline**：triage、maker/checker、run log、budget、escalation、stop condition 是 first-class。
- **Git-native team assets**：团队 AI 资产以代码仓库为底座，可版本化、可审计、可下发。
- **Local control and portability**：inspectable state files、export/import、无强制 cloud account。

---

## 6. 领域模型

```
团队 Team（可选；local-first 下的协作边界，经 git 仓库共享资产）
└─ 项目 Project（顶层空间容器，侧栏项目切换器）
   └─ 循环 Loop（1 项目 = 多 Loop，各自独立连续工作流；侧栏 Loop 切换器）
      └─ 目标 Goal（每 Loop 多个；各享 worktree 隔离 + Loop Engineering 六阶段）
         ├─ Run（Goal 的一次执行实例，含 trace / checkpoint / replay / validation receipt）
         └─ Handoff Packet（跨 agent/会话/团队的上下文打包，下一执行方直接续跑）
      ↑ 新建任务 Task = 用户意图入口，创建 Goal 并自动进入当前活跃 Loop
```

- **任务 Task（新建任务）🔲**：用户侧意图入口。`新建任务` = 在活跃 Loop 创建 Goal。必须归属项目（缺省当前）与 Loop（缺省当前活跃 Loop）。
- **目标 Goal ✅🔲**：Loop 内的 bounded 工作单元，享 worktree 隔离，走六阶段（分诊 → 制作 → 检查 → 升级 → 运行日志 → 停止）。状态机：planned / triage / maker / checker / escalated / stop。
- **Run 🆕**：Goal 的一次执行实例。产生 trace、cost、artifacts、validation receipt；interrupted run 可 resume/rewind。
- **循环 Loop ✅🔲**：项目内的连续工作流，跨多个 Goal 持续，持有连续上下文（memory / artifacts / run log）。
- **项目 Project ✅🔲**：顶层空间容器，承载独立上下文、状态与交付物。侧栏切换。
- **Handoff Packet 🆕**：跨 agent / 会话 / 团队的上下文契约（见 §11.3）。
- **团队 AI 资产 Asset 🆕**：Spec / Rule / Skill / MCP / Deliverable，git 化、可版本化、可下发。

> 命名纪律：统一使用 LoopDesk / loop_workspace / LOOP-STATE.json / Project / Loop / Goal / Task / Run / Handoff Packet；不暴露 legacy session / workspace-state.json / channel-first 文案。

---

## 7. 能力总览（九大平面）

| 平面 | 职责 | 关键能力 |
| --- | --- | --- |
| **Workspace & State** | 单一真相源 | `LOOP-STATE.json`、团队级上下文、Handoff Packet、export/import、公私边界 |
| **System Integration (MCP)** | 外部系统接入 | JIRA/Plane/Confluence/GitHub 连接器、双向同步、MCP lifecycle |
| **Agent Orchestration** | local-first 编排 | Agent 注册表、Task Router、worktree 隔离、并行/子会话、状态 rollup |
| **Loop Engine & Long Tasks** | 长任务自动完成 | Scheduler、triage/maker/checker、长任务模板、quota/gate、typed handoff、独立验证 |
| **Context & Memory** | 上下文传递 | 注入契约、跨会话/团队传递、三层记忆、白盒可编辑、compaction |
| **Team AI Assets** | 团队能力复用 | 资产注册表、git 共享、下发 Distributor、Skill Engineering |
| **Governance/Cost/Safety** | 治理与护栏 | trace schema、成本 rollup、预算/kill switch、审批、沙箱、失败模式 |
| **Surfaces** | 用户面 | CLI、本地 Web 控制中心、Agent Work Feed、IM、onboarding、机器可读文档 |
| **Learning** | 持续改进 | Continuous Learning Loop、decision 谱系、reward、friction 沉淀、KB Health |

---

## 8. 用户主流程与场景

### 8.1 主流程

1. 安装 CLI，`loopdesk onboard` 完成首次 setup（自动发现本地 Claude Code / Codex）。🔲
2. 初始化本地 loop workspace、`LOOP-STATE.json`、memory、skills、artifacts、worktree。✅
3. 通过 MCP-first、ACP-second 或 tool-specific adapters 连接工具与系统（JIRA/Plane/Confluence/GitHub）。✅⏳
4. LoopDesk 判断当前工作应继续 discovery、triage、synthesis，还是收敛成 bounded Goal。✅
5. 从 CLI / 本地 Web UI 查看 state；敏感动作需 explicit approval。✅
6. 离开主环境时，可通过 Web 或 IM 查看状态、approve/reject、继续 approved bounded work。🔲⏳
7. 结果、decisions、run history 回写本地 workspace，并回写外部系统（JIRA/Confluence/PR）。✅⏳
8. 开发者 / 另一位成员从 durable state 切换到其他工具或团队，无需重新粘贴上下文。✅🆕

### 8.2 核心场景

- **Scenario A — 任务与知识接入（约束 1）**：LoopDesk 经 MCP 连接器拉取 JIRA/Plane issue 与 Confluence 知识进入工作区，agent 执行时"`+` 引用"直接消费；完成后回写进度/结果/链接。
- **Scenario B — local-first 编排 agent（约束 2）**：从任务/知识生成 Goal；LoopDesk 在本地选择并调度 claude/codex/pi；每个 agent 在隔离 worktree 执行，带预算/权限/stop condition；控制中心统一展示所有会话、审批门待处理、运行任务。
- **Scenario C — 跨 agent / 会话 / 团队传递（约束 3）**：任务上下文以团队级 Workspace State 持久化；一个 agent 的部分工作通过 Handoff Packet 由下一执行方（不同工具/会话/成员）直接续跑；团队 A 的 Spec/Rule/交付物可经 git 作为上下文传入团队 B。
- **Scenario D — 团队 AI 资产下发（约束 4）**：资产注册表收录 Specs/Rules/Skills/MCP/交付物；Rules/Specs/Skills 支持 owner 一键下发（免安装、版本统一、可回滚）；MCP 配置与交付物随仓库共享。
- **Scenario E — 长任务模板自动完成（约束 5）**：内置 issue-fix / pr-commit / auto-research 模板，参数化选用；受 quota/gate 治理，关键关口人审批；形成固定骨架。
- **Scenario F — 团队协作复用 🆕**：成员通过 Big @ 引用他人/其他 agent 的历史与产物；借用队友的 agent 与 skills；房间级（workspace 级）隔离避免串扰。
- **Scenario G — 可观测与恢复 🆕**：Goal 时间线（Plan→Execute→Audit→Decision）；checkpoint/resume/rewind；确定性 replay；失败模式自动降级。

---

## 9. 功能清单（Feature Inventory）

> 本节是本次「功能最完整」交付的核心。每条含：ID / 功能 / 说明 / 优先级 / 状态 / 借鉴来源。
> 借鉴来源中用 `★` 标注 LoopDesk 独有或重点差异化能力。

### 9.1 工作区与状态内核（WS）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| WS-01 | `LOOP-STATE.json` 可移植真源 | 单一 durable source of truth，可机读、可 diff、可 export | P0 | ✅ | ★ LoopDesk |
| WS-02 | Project/Loop/Goal/Task/Run 领域模型 | 五层领域模型 + 状态机 | P0 | 🔲 | loop-engineering / Octos |
| WS-03 | 项目 / Loop 切换器 | 侧栏切换空间与连续工作流 | P1 | ✅ | ★ LoopDesk |
| WS-04 | Workspace State Protocol | memory/skills/artifacts/worktrees 同一边界 | P0 | ✅ | ★ LoopDesk |
| WS-05 | 团队级 Workspace State | 目标/决策/证据/待办/交接/配额，团队可 inspect | P0 | 🆕 | Tutti / LoopX |
| WS-06 | Handoff Packet | 跨 agent/会话/团队成员上下文打包 | P0 | 🆕 | LoopX typed handoff |
| WS-07 | partial export/import | 按 Goal / Loop / time range 导出，无云账号 | P0 | ✅ | Octos / Proma |
| WS-08 | 公私边界（public-private boundary） | 公开 schema/约定；私有路径/日志/凭证/活跃 goal 不提交 | P0 | 🆕 | LoopX |
| WS-09 | 白盒 human-readable 状态 | 所有状态文件 Markdown/JSON，可本地检查 | P0 | ✅ | PilotDeck / Trellis |

### 9.2 系统集成与 MCP 连接器（SYS）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| SYS-01 | MCP-first adapter | 工具/资源/prompt/事件统一建模，stdio + HTTP | P0 | ✅ | ★ LoopDesk |
| SYS-02 | ACP-second adapter | session-rich 工具用 ACP，不替代 MCP | P1 | ✅ | Octos / Buzz |
| SYS-03 | JIRA 连接器 | 任务拉取 + 进度/结果/链接回写 | P0 | 🆕 | 约束 1 |
| SYS-04 | Plane 连接器 | 同上，Plane 任务系统 | P0 | 🆕 | 约束 1 |
| SYS-05 | Confluence 连接器 | 页面/空间索引为项目知识，agent 可引用 | P0 | 🆕 | 约束 1 |
| SYS-06 | GitHub 连接器 | 资产/交付物/PR 共享与联动 | P0 | 🆕 | 约束 1/4 |
| SYS-07 | 双向同步 | inbound 事件→Workspace State；产出→外部系统 | P0 | 🆕 | 约束 1 |
| SYS-08 | MCP lifecycle per workspace | enable/disable/retry/recover/audit | P0 | ✅ | Proma / Octos |
| SYS-09 | MCP tool call traceability | 溯源到 workspace/Goal/run/approval/budget | P1 | 🆕 | Proma / Octos |
| SYS-10 | 连接器插拔扩展 | Linear/Notion/GitLab 等以 MCP Server 扩展 | P2 | 🆕 | Octos |
| SYS-11 | MCP 关键字路由 | per-tool routing keywords | P2 | 🆕 | DeerFlow / ruflo |

### 9.3 Agent 编排（ORCH）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| ORCH-01 | Agent 注册表 | provider/runtime/instructions/env/MCP/skills/最大并发 | P0 | 🆕 | 约束 2 / Multica |
| ORCH-02 | local-first 调度 | 在本地选择调度 claude/codex/pi，不取代其 runtime | P0 | 🆕 | 约束 2 |
| ORCH-03 | Task Router + human override | 按 intent/成本/历史选 agent，保留人工覆盖 | P0 | 🆕 | LoopX / PilotDeck |
| ORCH-04 | per-Goal worktree/scratch 隔离 | OS 级沙箱 + 路径限制 + 审计快照 | P0 | ✅ | emdash / Orca |
| ORCH-05 | 并行 agent + 赢家选择 | 一条 prompt 扇到多 agent 各 worktree，比较后合并 | P1 | 🆕 | Orca / emdash |
| ORCH-06 | 子会话/主会话 + 平行探索 | 分叉不污染主上下文，可一键带回；对抗性分析 | P1 | 🆕 | Proma |
| ORCH-07 | Agent 状态 rollup | blocked/working/done/idle/unknown，向 pane/loop 上卷 | P1 | 🆕 | Herdr |
| ORCH-08 | 真实 PTY 保留 | 不把 agent 输出重渲染为 chat UI | P1 | 🆕 | Herdr |
| ORCH-09 | detach/restore + native resume | 长任务抗断连，恢复原生会话 | P2 | 🆕 | Herdr / emdash(tmux) |
| ORCH-10 | session host authority | canonical PTY ownership、拒绝陈旧客户端等不变量 | P2 | 🆕 | Orca |
| ORCH-11 | Runtime capability profile | `execute/resume/status/cancel/inspect` + runtime matrix | P1 | ✅ | v1.2 runtime-matrix |
| ORCH-12 | 会话恢复保留 workdir | 保留 workdir + 对话历史供续跑 | P1 | 🆕 | Multica / WeSight |
| ORCH-13 | Runtime driver 抽象（含 dsh） | Profile/Bundle/Patch 可组合 runtime，保持 LOOP-STATE 独立 | P2 | 🆕 | DeepSeek Harness |

### 9.4 Loop 引擎与长任务（LOOP）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| LOOP-01 | Scheduler | cron / once / fire-immediate / durable / pause / kill | P0 | ✅ | loop-engineering |
| LOOP-02 | triage/maker/checker/escalation | 六阶段生命周期 | P0 | ✅ | loop-engineering |
| LOOP-03 | L1/L2/L3 成熟度分级 | 报告 → 辅助 → 无人值守渐进 | P0 | ✅ | loop-engineering |
| LOOP-04 | 长任务模板引擎 | 参数化选模板 → 生成 Goal 骨架 | P0 | 🆕 | 约束 5 / LoopX |
| LOOP-05 | issue-fix 模板 | 滚动仓库上下文 + 带版本修复知识 | P0 | 🆕 | LoopX showcase |
| LOOP-06 | pr-commit 模板 | 生成/打磨 PR 与提交 | P0 | 🆕 | LoopX showcase |
| LOOP-07 | auto-research 模板 | proposer→executor→evaluator 多角色迭代 | P0 | 🆕 | LoopX showcase |
| LOOP-08 | 自定义模板 / 模板市场 | 用户可自定义、可分享 | P2 | 🆕 | Tutti 应用生态 |
| LOOP-09 | Quota 决策 `should-run` | 运行前判定是否该跑 | P0 | 🆕 | LoopX |
| LOOP-10 | 五级 Gate | health → operator → evidence → focus → compute quota | P0 | 🆕 | LoopX |
| LOOP-11 | Typed turn 决策枚举 | route（执行前）+ result（执行后） | P1 | 🆕 | LoopX |
| LOOP-12 | Typed handoff packet | 结构化交接，跨 agent/会话/团队续跑 | P0 | 🆕 | LoopX |
| LOOP-13 | 独立验证 | checker fresh context / 只读 / 快照哈希 / validation receipt | P0 | 🆕 | LongHorizon / GOAI |
| LOOP-14 | 上下文剪枝 | 丢弃 execution history，仅带经审计 facts 进下一轮 | P1 | 🆕 | LongHorizon |
| LOOP-15 | checkpoint/resume/rewind/时间旅行 | 从 durable event log 恢复与回滚 | P1 | 🆕 | Octos |
| LOOP-16 | Goal 时间线 | Plan→Execute→Audit→Decision 卡片流 | P1 | 🆕 | LongHorizon |
| LOOP-17 | no-progress breaker | 无进展自动熔断 | P1 | 🆕 | DeerFlow |
| LOOP-18 | stop condition / completion criteria | 显式完成与停止 | P0 | ✅ | loop-engineering |
| LOOP-19 | Run log | started / found / acted / escalated / cost | P0 | ✅ | ★ LoopDesk |
| LOOP-20 | Quota 占空比记账 | duty cycle + window_hours + spent_slots | P1 | 🆕 | LoopX |
| LOOP-21 | 修复知识 / decision 谱系沉淀 | 带版本修复知识、决策链，提升同类任务质量 | P1 | 🆕 | LoopX decision context |

### 9.5 上下文传递与记忆（CTX）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| CTX-01 | Context Injection Contract | 跨工具 handoff 最小载荷（7 字段） | P0 | 🆕 | Terax / Raft（S8） |
| CTX-02 | 跨会话 continuity | resume / history / replay / export / abort | P0 | ✅ | Octos |
| CTX-03 | 跨团队上下文引用 | git 资产（Spec/Rule/Deliverable）作输入 | P1 | 🆕 | 约束 3 |
| CTX-04 | Big @ 跨代理引用 | 引用其他 agent/成员的历史、文件、应用调用、任务 | P1 | 🆕 | Tutti |
| CTX-05 | 代理借用 | 借用队友 agent 与 skills | P2 | 🆕 | Tutti |
| CTX-06 | 三层记忆 | person（偏好）/ event（工作记录）/ experience（可复用方法） | P1 | 🆕 | Zleap |
| CTX-07 | 白盒可编辑记忆 | 可查/改/删/钉住决策，避免全局污染 | P1 | 🆕 | PilotDeck |
| CTX-08 | Memory Dream 后台提炼 | 周期/阈值触发抽取可复用经验 | P2 | 🆕 | Zleap |
| CTX-09 | 记忆条目 schema | topic / fact / source / confidence / updated_at / links | P1 | 🆕 | 各竞品（S9） |
| CTX-10 | compaction + superseded-read elision | 长会话压缩，非简单丢弃 | P1 | ✅ | Octos / Terax |
| CTX-11 | Human Model | 偏好/决策模式/review standard，local-first | P1 | 🔲 | v1.1 |
| CTX-12 | 本地检索 | keyword + semantic + BM25 图增强重排 | P1 | ✅ | TeamAI |
| CTX-13 | 记忆按人隔离 | 开发者 journal 分人，共享 spec/task 入 git | P2 | 🆕 | Trellis |

### 9.6 团队 AI 资产（ASSET）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| ASSET-01 | 资产注册表 | Spec / Rule / Skill / MCP / Deliverable 五类统一建模 | P0 | 🆕 | 约束 4 |
| ASSET-02 | Git 仓库共享 | clone/pull/push，资产即可版本化文件 | P0 | 🆕 | 约束 4 / TeamAI |
| ASSET-03 | 下发 Distributor | Rules/Specs/Skills 一键 push 到成员工作区，免安装 | P0 | 🆕 | Proma 企业版 |
| ASSET-04 | 资产版本管理/审计/回滚 | 版本锁定、审计、可回滚 | P0 | 🆕 | Proma / TeamAI |
| ASSET-05 | 资产发现/检索/复用 | Skills Hub 式发现，但 local-first | P1 | 🆕 | Proma / Octos |
| ASSET-06 | Skill Engineering | trigger / context / workflow / evaluation / feedback | P0 | ✅ | ★ LoopDesk |
| ASSET-07 | Skill 组织级分发 | 统一版本、免安装、使用范围控制 | P0 | 🆕 | Proma `PROMA-MANAGER-MCP` |
| ASSET-08 | 分发范围控制 | roles（role→namespace）/ tags（标签订阅）/ sources（订阅外部源） | P1 | 🆕 | TeamAI |
| ASSET-09 | 声明式 team hooks/MCP YAML | 一次声明 `${VAR}` 注入，pull 翻译为各工具原生格式 | P2 | 🆕 | TeamAI |
| ASSET-10 | SessionStart 自动 pull | hook 自动同步资产到各工具目录 | P1 | 🆕 | TeamAI |
| ASSET-11 | 资产复用度量 | 下发后实际复用比例、KB Health | P2 | 🆕 | TeamAI |
| ASSET-12 | Deliverable 共享 | 交付物随仓库共享（不强制下发） | P1 | 🆕 | 约束 4 |
| ASSET-13 | 真源 + 派生生成 | 一处定义，生成/同步到各工具，保留用户编辑 | P2 | 🆕 | Trellis |
| ASSET-14 | 工作流状态机 + 回归守护 | 防 AI 静默跳过必做步骤 | P2 | 🆕 | Trellis |

### 9.7 治理、成本与安全（GOV）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| GOV-01 | Execution Trace / Run Log schema | action/tool/runtime/duration/cost/decision/result/artifacts | P0 | ✅ | v1.2 F4 / DeerFlow |
| GOV-02 | 成本跟踪 + rollup | 按 session/agent/skill/loop/team 汇总 | P0 | ✅ | Octos swarm ledger |
| GOV-03 | 预算上限/日限/max iterations/kill switch | 硬护栏 | P0 | ✅ | loop-engineering |
| GOV-04 | 审批队列 + 多端审批 | CLI/Web/IM 同一 local audit trail | P0 | ✅ | ★ LoopDesk |
| GOV-05 | Escalation | ambiguity / repeated failure / denylist 路径 | P0 | ✅ | loop-engineering |
| GOV-06 | 权限模式 | read-only / restricted / full-access | P0 | ✅ | Octos |
| GOV-07 | 沙箱 | worktree / bwrap / sandbox-exec / Docker | P1 | ✅ | Octos / DeerFlow |
| GOV-08 | deny-wins tool policy + path denylist | `.env`/secrets/production 路径拒绝 | P0 | ✅ | Octos / loop-engineering |
| GOV-09 | 五层安全语法 | IPC / fs / network / secret / terminal-escape 分别设防 | P1 | 🆕 | Terax |
| GOV-10 | secrets 保护 | 不进 prompt/state/logs；OS keychain 存储 | P0 | ✅ | Terax / loop-engineering |
| GOV-11 | hash-chain / ledger 审计日志 | 篡改可检测 | P2 | 🆕 | Buzz / Zleap |
| GOV-12 | 失败模式目录 + kill/降级规则 | 见 §13 | P0 | 🆕 | loop-engineering（S11） |
| GOV-13 | 团队额度管理 | 分配/回收/月自动/用量流水（Proma 对标，git 原生替代 Cloud） | P1 | 🔶 | Proma 企业版 |
| GOV-14 | Cloud API Key 额度上限（预留） | 仅预留接口，不做 SaaS 计费核心 | P2 | 🔲 | Proma 企业版 |
| GOV-15 | 独立验证凭证 | 机器可读 Validation Receipt | P0 | 🆕 | GOAI / LongHorizon |
| GOV-16 | 审计控制头契约 + 格式修复 | Status / Integrity / Contract audit 三行头 | P1 | 🆕 | LongHorizon |

### 9.8 用户面与分发（SURF）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| SURF-01 | CLI（`loopdesk`） | 安装、setup、state inspection、handoff | P0 | ✅ | ★ LoopDesk |
| SURF-02 | 本地 Web UI 控制中心 | setup / inspection / approval / diagnostics / replay / export | P0 | ✅ | ★ LoopDesk |
| SURF-03 | Agent Work Feed | 推荐式卡片：产出/为何关注/证据/quota 成本/建议下一步/一键反馈 | P1 | 🆕 | LoopX |
| SURF-04 | 统一运行视图 | 所有 agent 会话、审批门待处理、运行任务、资产状态、长任务进度 | P0 | ✅ | Multica / Tutti |
| SURF-05 | IM 继续面 | DingTalk/Feishu/Slack/WeCom；disabled-by-default | P1 | ⏳ | cc-connect |
| SURF-06 | Desktop 打包 | macOS/Windows/Linux | P2 | 🔲 | ★ LoopDesk |
| SURF-07 | Guided onboarding | 5 分钟内完成首个有用 Goal，无关键术语障碍 | P0 | 🔲 | Cindy / Raft |
| SURF-08 | 机器可读文档 | `/llms.txt` + `/<page>.md`，供 agent 消费 | P2 | 🆕 | Raft Docs |
| SURF-09 | 团队资产 / 长任务面板 | 资产分发状态、模板运行进度 | P1 | 🆕 | Proma / Multica |
| SURF-10 | goal 时间线视图 | 六阶段 stepper + trace 事件 + resume/rewind 入口 | P1 | 🆕 | LongHorizon |
| SURF-11 | annotate diff / per-hunk accept | 直接在 AI diff 上注释回传 | P2 | 🆕 | Orca / Terax |
| SURF-12 | 任务看板（默认落地） | Codex 三栏布局；默认进入任务看板，按项目切换 | P0 | 🆕 | Codex 范式 |
| SURF-13 | 资产市场（Marketplace） | 团队资产以市场形态呈现；个人用户只读浏览 rules/commands/skills/mcp，默认按项目筛选 | P0 | 🆕 | Proma / Codex 扩展心智 |

### 9.9 学习与持续改进（LEARN）

| ID | 功能 | 说明 | 优先级 | 状态 | 借鉴来源 |
| --- | --- | --- | --- | --- | --- |
| LEARN-01 | Continuous Learning Loop | loop 结束后沉淀经验进 memory/skills | P1 | 🆕 | loop-engineering |
| LEARN-02 | completed Goal → knowledge flush | 已完成任务知识写入 memory | P1 | ✅ | ★ LoopDesk |
| LEARN-03 | reward 模型 | 输出量/质量/token/注意力成本保守评估 | P2 | 🆕 | LoopX |
| LEARN-04 | friction 信号驱动沉淀 | 打断/纠正/重试失败触发沉淀，例行会话不触发 | P2 | 🆕 | TeamAI |
| LEARN-05 | KB Health | 置信剪枝/陈旧标记/回写分数/召回趋势 | P2 | 🆕 | TeamAI |
| LEARN-06 | decision context / 决策谱系 | 基于证据与已验证结果重定基决策 | P1 | 🆕 | LoopX |
| LEARN-07 | anchor packet | issue/PR → 带证据边界的可复用 candidate | P2 | 🆕 | LoopX |
| LEARN-08 | GOAP 目标分解 + plan tree | 自然语言目标 → precondition/effect/rollback 计划 | P2 | 🆕 | ruflo |

### 9.10 功能清单统计

| 分类 | 条目数 | P0 | P1 | P2 |
| --- | --- | --- | --- | --- |
| WS 工作区与状态内核 | 9 | 7 | 1 | 0 |
| SYS 系统集成与 MCP | 11 | 8 | 2 | 2 |
| ORCH Agent 编排 | 13 | 4 | 6 | 3 |
| LOOP Loop 引擎与长任务 | 21 | 9 | 8 | 1 |
| CTX 上下文与记忆 | 13 | 2 | 8 | 3 |
| ASSET 团队 AI 资产 | 14 | 6 | 5 | 3 |
| GOV 治理/成本/安全 | 16 | 10 | 4 | 2 |
| SURF 用户面与分发 | 11 | 5 | 3 | 3 |
| LEARN 学习与改进 | 8 | 0 | 3 | 5 |
| **合计** | **116** | **51** | **40** | **22** |

---

### 9.11 前端信息架构与页面功能清单（Codex 三栏范式重构）🆕

> 本节**替代**原「Web UI Page Inventory」。重构目标：**让一般程序员一进来就能用**，同时不牺牲专业性。
> 参考范式：**Codex 三栏布局 + 设置对话框**（程序员已熟悉的心智，无需学习成本）。
> 状态图例同 §9。`UI-*` 为页面/交互 ID。

#### 9.11.1 优化建议（旧 → 新）

| 旧设计问题（偏专业、难上手） | 新设计建议（一般程序员视角） |
| --- | --- |
| 把 Loop / Goal / Quota / Gate / Handoff / Validation Receipt 等后端术语直接搬上前端 | **术语分层**：一级界面只说人话（任务 / 看板 / 对话 / 变更 / 成本 / 审批），专业术语下沉到右栏、详情、设置**按需展开** |
| 页面分散（工作台 / 新建任务 / Goal 时间线 / Agents / Sessions / Skills / Assets… 各自独立页） | **收敛为三栏**：左=导航+任务列表，中=任务看板/详情，右=上下文；其余全部进入设置 |
| 默认落地是"工作台仪表盘"，普通程序员不知道先干什么 | **默认落地 = 任务看板**（按项目切换），一进来就看到"我的任务"，与 GitHub Projects / Trello 同构 |
| 资产中心像内部注册表，个人用户无从下手 | **团队资产 = 市场（Marketplace）**：个人用户**只读**浏览 rules / commands / skills / mcp，**默认按项目筛选** |
| 配置项散落多处 | **统一设置入口**：点击设置图标 → Codex 风格设置界面（左分类 + 右表单） |
| 专业性靠术语堆砌 | **专业性靠可见护栏**：审批队列、预算条、变更 diff、验证徽标、运行日志——看得见才可信 |

#### 9.11.2 整体布局：Codex 三栏（全局恒定）

```
┌───────────────┬───────────────────────────────┬──────────────────────┐
│  左栏 导航     │  中栏 主工作区                 │  右栏 上下文(可折叠)   │
│  240px         │                               │  360px               │
│               │  顶部：项目名 · 搜索 · +新建    │                      │
│ ▾ 项目切换器   │                               │  当前任务概览         │
│               │  ┌── 任务看板（默认落地）──┐   │  ├ 进度（简化/六阶段） │
│ 任务           │  │ 待办│进行中│评审中│完成 │   │  ├ 成本 / 预算        │
│  · 待办 3      │  │ ┌──┐┌──┐┌──┐┌──┐      │   │  ├ 审批门             │
│  · 进行中 2    │  │ │卡││卡││卡││卡│      │   │  ├ 变更 diff          │
│  · 评审中 1    │  │ └──┘└──┘└──┘└──┘      │   │  ├ Agent / 会话       │
│  · 已完成 12   │  └────────────────────────┘   │  └ 证据 / 验证 ▸      │
│               │                               │                      │
│ 资产市场 🛍     │                               │                      │
│ 设置 ⚙         │                               │                      │
└───────────────┴───────────────────────────────┴──────────────────────┘
```

三栏职责：
- **左栏**：项目切换器（切换看板）+ 任务列表（按状态）+ 底部导航（任务 / 资产市场 / 设置）。
- **中栏**：默认任务看板；点开任务 → 任务详情（对话流 + 工具调用 + 交付物）；新建任务在此发起。
- **右栏**：当前任务的上下文面板，可折叠；承载专业信息（进度、成本、审批、diff、证据）。
- **顶部**：项目名、搜索、`+ 新建任务`、设置图标。

> **列名口径（2026-09-14 冻结）**：看板第三列为 **评审中**，不叫"待审批"。人工把关的 **审批门（operator gate）** 是**列内的卡点**，落在右栏 UI-R4 区块（琥珀色 + 数量摘要，默认折叠），不单独占一列——"评审中"是状态，"审批门"是卡在其中的动作。
>
> **本次对齐范围**：上表 L2 / L5 / C1 / R4 四处原用「待审批」的表述已按上述口径改写；依据为 `AGENTS.md` §4.4 画布修订 v2 的裁决与主画布 `724693301521075` 实测节点（`Col 评审中` = `2:90`、`Accordion · 审批门（三级·默认折叠）` = `2:213`）。
>
> **左栏现状 ≠ 上图目标态**：上图左栏的"按状态分组任务列表 + 审批门红点"是 **PRD 目标**；主画布 `2:2` 当前左栏为「品牌 / 新建任务 / 会话·渠道 / 导航（任务看板 · 团队资产 · 控制中心 · 设置）/ 项目列表」，**尚未包含该列表与红点**（记为 L2 / L5 缺失，见 `docs/design-system/frontend-vs-prd-audit.md`）。两栏宽度亦已按画布实测校正为 **240 / 360**（原写 `~260` / `~320`）。

#### 9.11.3 左栏（导航）

| ID | 组件 | 功能 | 优先级 | 状态 |
| --- | --- | --- | --- | --- |
| UI-L1 | 项目切换器 | 下拉切换项目，看板与上下文随项目切换 | P0 | ✅ |
| UI-L2 | 任务列表 | 按状态分组（待办 / 进行中 / 评审中 / 已完成），可搜索 | P0 | ✅ |
| UI-L3 | 新建任务 | 列表顶部入口，发起任务 | P0 | ✅ |
| UI-L4 | 底部导航 | 任务 / 资产市场 / 设置 ⚙（三入口收敛） | P0 | 🔶 |
| UI-L5 | 审批门徽标 | 审批门待处理数量红点，点击定位到右栏「审批门」区 | P0 | ✅ |
| UI-L6 | 折叠 / 主题 | 折叠侧栏；Light / Dark | P1 | ✅ |

#### 9.11.4 中栏：任务看板（默认落地）与任务详情

| ID | 组件 | 功能 | 优先级 | 状态 |
| --- | --- | --- | --- | --- |
| UI-C1 | 任务看板 | **默认落地**；四列等宽：待办 / 进行中 / 评审中 / 已完成 | P0 | 🆕 |
| UI-C2 | 任务卡 | 标题、项目、模板、Agent、状态、成本、下一步建议 | P0 | 🆕 |
| UI-C3 | 看板筛选 / 搜索 | 按项目 / 状态 / 模板 / Agent 筛选与搜索 | P1 | 🆕 |
| UI-C4 | 新建任务面板 | 选模板（issue-fix / pr-commit / auto-research / 自由）+ 一句话描述 → 进入执行 | P0 | ✅ |
| UI-C5 | 任务详情 | 对话流 + 工具调用卡 + 交付物卡（点开任务后） | P0 | ✅ |
| UI-C6 | 进度（简化） | 面向用户：分诊 → 执行 → 检查 → 完成 | P0 | ✅ |
| UI-C7 | 空 / 加载 / 错误态 | 全覆盖，含首次引导（无任务时提示新建） | P0 | ✅ |

#### 9.11.5 右栏：上下文面板

| ID | 组件 | 功能 | 优先级 | 状态 |
| --- | --- | --- | --- | --- |
| UI-R1 | 任务概览 | 标题、项目、模板、Agent、发起时间 | P0 | 🆕 |
| UI-R2 | 进度明细 | 六阶段 stepper（专业版；普通用户默认折叠为四项） | P0 | ✅ |
| UI-R3 | 成本 / 预算 | Spend / Budget 进度条 + 超预算告警 | P0 | ✅ |
| UI-R4 | 审批门（Gate） | 审批队列（approve / deny）+ 一键处理；三级术语，默认折叠 | P0 | ✅ |
| UI-R5 | 变更 diff | 逐 hunk accept / reject + 注释回传 | P1 | 🆕 |
| UI-R6 | Agent / 会话 | 当前 Agent、状态 rollup、会话恢复 | P1 | 🆕 |
| UI-R7 | 证据 / 验证 | validation receipt、integrity 徽标（按需展开） | P1 | 🆕 |
| UI-R8 | Handoff | 交接给其他 agent / 成员 / 工具 | P1 | 🆕 |

#### 9.11.6 团队资产市场（Marketplace）

| ID | 组件 | 功能 | 优先级 | 状态 |
| --- | --- | --- | --- | --- |
| UI-M1 | 市场入口 | 左栏底部导航「资产市场」→ 市场页 | P0 | 🆕 |
| UI-M2 | 资产卡片 | 名称、类型（rule / command / skill / mcp）、作者、版本、说明、适用项目 | P0 | 🆕 |
| UI-M3 | 默认项目筛选 | **默认只显示当前项目适用的资产** | P0 | 🆕 |
| UI-M4 | 只读浏览（个人用户） | 个人用户**仅查看**，不提供编辑入口 | P0 | 🆕 |
| UI-M5 | 安装 / 启用 | 有权限用户可安装到项目；个人用户看"已启用"状态 | P1 | 🆕 |
| UI-M6 | 下发（owner / admin） | 一键推送到成员工作区、版本锁定、回滚 | P1 | 🆕 |
| UI-M7 | 资产详情 | 版本历史、diff、来源 git、使用范围 | P1 | 🆕 |
| UI-M8 | 搜索 / 分类 | 按类型、标签检索 | P1 | 🆕 |

> 心智：与 Codex / VS Code 的「扩展市场」一致——普通用户是消费者，看得到、装得上、不被迫理解治理细节。

#### 9.11.7 设置（Codex 风格，点击设置进入）

| ID | 分类 | 功能 | 优先级 | 状态 |
| --- | --- | --- | --- | --- |
| UI-S1 | 设置入口 | 顶部 / 左栏 ⚙，点击进入设置界面（左分类 + 右表单） | P0 | ✅ |
| UI-S2 | 通用 | 语言、主题、启动项、默认项目 | P0 | ✅ |
| UI-S3 | 模型与 Provider | 渠道、模型、能力、限流、用量 | P0 | ✅ |
| UI-S4 | Agent | Agent 注册表（runtime / 指令 / env / 并发） | P1 | 🆕 |
| UI-S5 | 连接器（MCP） | JIRA / Plane / Confluence / GitHub 启停 / 重试 / 审计 | P1 | 🆕 |
| UI-S6 | 审批与安全 | 权限模式、path denylist、沙箱、secrets | P0 | ✅ |
| UI-S7 | 用量与额度 | 成本 rollup、预算、团队额度 | P1 | ✅ |
| UI-S8 | 团队 | 成员、角色、额度池、分发范围 | P1 | 🔶 |
| UI-S9 | 模板管理 | 长任务模板（内置 / 自定义） | P1 | 🆕 |
| UI-S10 | 外观 | Light / Dark、密度、图标 | P1 | ✅ |
| UI-S11 | 高级 | 网关、网络、诊断、日志、导出 | P0 | ✅ |

#### 9.11.8 术语可见性分层（专业性如何体现）

| 层级 | 出现位置 | 用词 | 目的 |
| --- | --- | --- | --- |
| 一级（默认可见） | 左栏 / 看板 / 卡片 | 任务、看板、对话、变更、成本、审批 | 程序员零学习成本 |
| 二级（右栏 / 详情） | 任务详情 / 右栏 | 模板、Agent、进度、证据、diff | 需要时可见 |
| 三级（按需展开 / 设置） | 展开区 / 设置 | Loop / Goal / Quota / Gate / Handoff / Validation Receipt | 保留专业深度，不挡新用户 |

> 专业性不靠术语，而靠**可见护栏**：审批队列、预算条、变更 diff、验证徽标、运行日志——让用户"看得见、控得住、信得过"。

#### 9.11.9 页面统计与约束

| 分组 | 组件数 | P0 | P1 |
| --- | --- | --- | --- |
| 左栏 导航 | 6 | 5 | 1 |
| 中栏 看板与详情 | 7 | 6 | 1 |
| 右栏 上下文 | 8 | 4 | 4 |
| 团队资产市场 | 8 | 4 | 4 |
| 设置 | 11 | 6 | 5 |
| **合计** | **40** | **25** | **15** |

> **前端设计约束**：
> - **三栏恒定**：无论用户多专业，主界面始终是三栏；专业能力通过右栏/设置渐进披露，不新增顶层页面。
> - **任务为中心**：默认落地任务看板，按项目切换；Loop/Goal 是后端边界，前端不拆页。
> - 状态用**文本 + 颜色**（无障碍）；单区块单主操作；破坏性操作需确认；全键盘可操作；对比度 ≥4.5:1。
> - Design tokens 一律取自 `docs/design-system.md`；本清单只定义结构与行为。
> - 响应式：Desktop 三栏 → Tablet 收起右栏 → Mobile 单列（左栏转底部标签栏）。
>
> **前端覆盖度 ≠ 上表"状态"列**：上表"状态"指**产品能力状态**（✅ 已实现 / 🔶 待验收 / 🆕 新增），**不是**前端实现覆盖率。前端覆盖度见 `docs/design-system/frontend-vs-prd-audit.md`（2026-09-14 二次复核 · 可用口径 **17 / 10 / 13**：完整 / 部分 / 缺失）。两者勿混用。
>
> **落地状态**：`docs/plans/loopdesk-webui-design-spec.md` 已升级为 **v2.0（Codex 三栏范式）**；`docs/web-ui.md` 已按 v2.0 重写；`docs/web-ui-menu-and-loop-workspace.md`（v0.1 菜单大纲）已于 2026-09-12 删除。

---

## 10. 需求详述（MUST / SHOULD）

### 10.1 Runtime（CLI + 本地网关）✅
- runtime MUST 初始化并管理本地 gateway 与 workspace directory。
- runtime MUST 暴露 loop state、run log、approvals、memory、skills、artifacts、assets、cost、diagnostics。
- runtime MUST 支持本地文件访问、worktree creation、agent lifecycle、restart/recovery。
- runtime 除 optional IM transports 与 provider API 外，core workflow SHOULD 支持 offline。

### 10.2 Workspace State Protocol ✅
- 系统 MUST 维护 `LOOP-STATE.json` 作为 portable source of truth。
- 系统 MUST 把 memory、skills、artifacts、worktrees、assets 放在同一 workspace boundary。
- 系统 MUST 支持 partial export/import，且不强制 cloud account。
- 系统 MUST 维护公私边界（WS-08）。

### 10.3 项目与多 Loop 模型 🔲
- 系统 MUST 支持项目作为顶层空间容器（独立上下文/状态/交付物）。
- 系统 MUST 支持每项目下多个独立 Loop，各自持有连续上下文。
- 系统 MUST 提供项目切换器与 Loop 切换器，切换即切换 Workspace 渲染的上下文。
- 新建任务 MUST 归属项目（缺省当前）与 Loop（缺省当前活跃 Loop）。

### 10.4 系统集成与 MCP（约束 1）🆕
- 系统 MUST 以 MCP-first 集成外部系统；对工具/资源/prompt/事件统一建模。
- 系统 MUST 提供默认任务连接器 JIRA、Plane（拉取 + 回写）。
- 系统 MUST 提供默认知识连接器 Confluence（索引/检索页面空间为项目知识）。
- 系统 MUST 提供 GitHub 连接器（资产/交付物/PR）。
- 系统 SHOULD 允许连接器以 MCP Server 形式插拔扩展。
- 系统 MUST 把 inbound 事件翻译为 Workspace State，并把产出翻译回外部系统。

### 10.5 Agent 编排（约束 2）🆕
- 系统 MUST 在 local-first 前提下注册并调度多个 agent，不取代其 runtime。
- 系统 MUST 维护 agent 注册表（provider/runtime/instructions/env/MCP/skills/最大并发）。
- 系统 MUST 支持按任务类型/成本/历史结果选择 agent；调度保留 human override，不允许无界自动路由。
- 系统 MUST 在隔离 worktree/scratch 中执行，带审批、预算上限与 stop condition。
- 系统 MUST 暴露统一控制中心视图（会话、审批门待处理、运行任务）。

### 10.6 跨 agent / 会话 / 团队上下文（约束 3）🆕
- 系统 MUST 以团队级 Workspace State 持久化上下文（目标/决策/证据/待办/交接/配额）。
- 系统 MUST 支持 Handoff Packet：一个执行方完成的上下文可被下一执行方直接消费续跑。
- 系统 MUST 支持跨会话连续性（resume/history/replay/export/abort）。
- 系统 SHOULD 支持跨团队上下文引用（经 git 共享的资产作为输入）。
- **Context Injection Contract**：handoff 时 MUST 自动构建并注入最小载荷（从 `LOOP-STATE.json` + memory + skills + active Goal 派生）：
  - `project_rules`：项目编码约定、架构约束、不可变决策
  - `recent_decisions`：近 N 次 run 的决策摘要（decision / rationale / evidence refs）
  - `active_goal`：intent、stop condition、当前阶段、budget 剩余
  - `next_action`：建议的下一 safe action（或"等待人工审批"）
  - `artifact_refs`：相关 artifacts（路径 + 摘要）
  - `cost_safety_summary`：已花费成本、safety posture、pending approvals
- 该载荷 MUST human-readable / diff-friendly，支持 partial export by Goal/Loop/time range。

### 10.7 团队 AI 资产管理（约束 4）🆕
- 系统 MUST 建立团队 AI 资产注册表：Spec、Rule、Skill、MCP 配置、Deliverable。
- 系统 MUST 支持资产经 GitHub 等代码仓库共享（clone/pull/push），资产即可版本化文件。
- 系统 MUST 支持 Rules、Specs、Skills 的"下发（distribute/push）"：owner/管理员推送到成员工作区，免安装、统一版本、可回滚。
- 系统 SHOULD 对资产做版本管理、审计与使用范围控制（roles/tags/sources）；MCP 配置与交付物随仓库共享但不强制下发。
- 系统 SHOULD 支持资产发现/检索/复用（类似 Skills Hub，local-first）。

### 10.8 Loop Engine 与长任务（约束 5）🆕
- 系统 MUST 支持 scheduled、fire-immediate、durable、controllable loops。
- 系统 MUST 实现 triage、maker、checker、escalation。
- 系统 MUST 记录 run log：started、found、acted、escalated、cost。
- 系统 MUST enforcing stop conditions 与 completion criteria。
- 系统 MUST 提供长任务模板引擎，内置至少 issue-fix / pr-commit / auto-research。
- 系统 MUST 让模板可参数化选用（选模板 → 填参 → 运行）。
- 系统 MUST 对长任务实施 quota/gate 治理：`should-run`、五级 gate、typed turn 结果枚举、typed handoff。
- 系统 MUST 为长任务记录 run log（证据、验证状态、阻塞项、已接受 writeback），可审计、可重启、可交接。
- 系统 SHOULD 沉淀带版本修复知识 / 决策谱系 / reward 信号。
- **独立验证**：checker MUST 以 fresh context 运行、只读（或 worktree 内）、可对 workspace 快照做哈希校验；Goal 完成 MUST 产生机器可读 validation receipt（criteria、evidence refs、checker run id）。
- **上下文剪枝**：每个 Goal run 结束后，SHOULD 将未验证的中间过程从连续上下文移除，只保留 verified facts、decisions、artifacts 与 next action 进入下一 run。

### 10.9 Memory 与 Context Continuity ✅
- 系统 MUST 提供 durable memory 与本地搜索（keyword + semantic）。
- 系统 MUST 支持 loop/goal run continuity：compact、cache continuity、resume、history、export、replay、abort。
- 系统 MUST 支持把 completed goal 知识 flush 进 memory。
- 系统 SHOULD 支持三层记忆（person / event / experience）与白盒编辑（CTX-06/07）。
- 命名约束：不暴露 legacy session 文案；连续状态统一以 loop / goal / run 表达。

### 10.10 Skills ✅
- 系统 MUST 支持 reusable skills 与 meta-skills。
- 系统 MUST 支持 inspection、replay、audit。
- 系统 SHOULD 支持基于 task context 的 skill auto-triggering。
- Skills MUST 绑定 cross-tool loop context，而非单客户端内部 workflow。

### 10.11 Runtime Visibility and Control ✅
- 系统 MUST 提供本地 inspection：active runs、approvals、logs、errors、memory、skills、worktrees、assets。
- 系统 MUST 提供 local web UI：guided setup、inspection、approval、diagnostics。
- Web MUST 保持 secondary，且不得替代本地 gateway authority。

### 10.12 Safety and Cost ✅🆕
- 系统 MUST 跟踪 token 与 cost（按 session/agent/skill/loop/team rollup）。
- 系统 MUST enforcing budget caps、daily limits、max iterations、kill switches。
- 系统 MUST 提供 approval queue，CLI/Web/IM 审批记录在同一 local audit trail。
- 系统 MUST 支持 escalation（ambiguity / repeated failure / denylisted paths）。
- 系统 MUST 实现 deny-wins tool policy、path denylist、secrets 保护。
- 系统 SHOULD 支持五层安全语法（IPC/fs/network/secret/terminal-escape）。
- 系统 MUST 维护公私边界（不提交凭证、私有日志、活跃 goal 状态）。

### 10.13 Isolation ✅
- 系统 MUST 支持 per-goal worktree 或 scratch directory。
- 系统 MUST 支持 cleanup 或 retained audit snapshots。
- 系统 MUST 避免 cross-loop workspace corruption。
- Remote surfaces MUST NOT bypass worktree isolation 或 local safety controls。

### 10.14 IM Remote Control ⏳
- IM adapters MUST disabled-by-default。
- IM 默认只读 inspection；write actions 需要显式 enablement、allowlist、approval-gating。
- IM MUST 支持 workspace selection、status、compact run summaries、approve/reject、bounded follow-up。
- IM MUST NOT 引入 team-room semantics、chat-first loop execution、unbounded shell access。

### 10.15 分发与部署 🆕
- CLI + web-guided install 为当前主路径。
- 原生桌面 installers/packages 为 v2.x 打包目标（不引入额外产品叙事）。
- 系统 MUST 在 upgrade/rollback 时保留本地 workspace data。
- 默认 gateway binding 为 `127.0.0.1`；public exposure 需要 explicit opt-in + auth + network controls。
- 团队资产分发 MUST 以 git 原生为底座，云同步仅作可选。

---

## 11. 关键契约与 Schema

### 11.1 `LOOP-STATE.json`（可移植真源）✅
最小字段：`project_id`、`loop_id`、`active_goal`（intent/goal_id/stage/budget_remaining/stop_condition）、`last_run`（run_id/status/last_action/outcome/cost）、`pending_decisions`、`human_overrides`、`last_updated`、`schema_version`。MUST human-readable / diff-friendly。

### 11.2 Execution Trace / Run Log 🆕
最小字段：`action`、`tool_or_runtime`、`duration`、`cost`、`decision`、`result`、`artifacts`、`verification`（maker_run_id / checker_run_id / verification_independent / integrity）。查询轴：Goal / Loop / time range。消费路径：replay / export / metrics。

### 11.3 Handoff Packet 🆕
`from`（agent/session/member）→ `to`、`active_goal`、`recent_decisions`、`artifact_refs`、`next_action`、`cost_safety_summary`、`gate_state`。MUST typed、可 diff、可部分导出。

### 11.4 Team Asset Manifest 🆕
`asset_id`、`type`（spec/rule/skill/mcp/deliverable）、`version`、`owner`、`scope`（roles/tags）、`source_git`、`distribute_policy`（push / shared-only）、`rollback_to`。

### 11.5 Memory Entry 🆕
`topic`、`fact`、`source`（tool + run）、`layer`（person/event/experience）、`confidence`、`updated_at`、`linked_artifacts`、`pinned`。

---

## 12. 成功指标

| 指标 | 定义 | 数据源 | 目标 |
| --- | --- | --- | --- |
| Context re-entry time | 跨工具/成员切换后重新解释上下文所需时间 | trace `context_injection` + opt-in survey | ≤ 手动 handoff 的 30%；注入契约覆盖率 ≥ 90% |
| Loop completion rate | Goal 达到 stop condition 的比例 | `run.log` status=stop / 总数 | ≥ 80% |
| Cross-tool fidelity | handoff 保留 state/decisions/artifacts 的比例 | §10.6 注入载荷字段完整度 | ≥ 90% |
| 跨团队成员交接成功率 | handoff packet 被下一成员直接续跑的比例 | handoff 事件 / 续跑事件 | ≥ 85% |
| 资产复用率 | Rules/Specs/Skills 下发后被成员实际复用的比例 | 资产 pull/使用事件 | ≥ 70% |
| 长任务完成率 | issue-fix/pr-commit/auto-research 达 stop condition 比例 | 模板 run log | ≥ 75% |
| Cost predictability | run 落在 budget/gate 阈值内的比例 | trace cost vs budget_cap | ≥ 85% |
| Remote approval latency | IM approval request → run log 记录决策 | `approval.requested_at`→`decided_at` | p50 ≤ 5min, p95 ≤ 30min |
| Recovery success | interrupted run 恢复且无 state corruption | resume 事件 + corruption 标志 | ≥ 95% |
| Onboarding completion | 首次 setup 完成"项目/Loop 选择 + resume 或新建 Goal" | `loopdesk onboard` 事件 | ≥ 70% 于 5 分钟内 |
| 独立验证可信度 | validation receipt 中 checker≠maker 且 integrity=clean 比例 | trace verification | ≥ 95% |

---

## 13. 失败模式目录与风险缓解

> 来源：`docs/research/loop-engineering.md` §5、LongHorizon、Buzz、S11。

| 失败模式 | 严重度 | 检测信号 | 缓解 | kill / 降级规则 |
| --- | --- | --- | --- | --- |
| Infinite Fix Loop | 🔴 高 | 连续 3 次 run 后同 Goal `last_action` 未变且仍 maker | maker/checker 分离；checker fresh context | 3 次失败 → escalation → 人工介入 |
| State Rot | 🔴 高 | `last_updated` 距今 > X 且无新动作 | compaction / prune（清理 superseded reads） | 24h 无更新 → auto-pause → 人工确认 |
| Verifier Theater | 🔴 高 | validation receipt 中 `checker_run_id == maker_run_id` | 强制独立验证：checker fresh context + integrity 快照哈希 | 同 run id → escalation |
| Notification Fatigue | 🟡 中 | approval 积压 > N 且 duration > M | compact notification；仅高严重度升级 | 7 天积压告警 → 审查阈值 |
| Token Burn | 🔴 高 | 单 run cost > budget×50% 或日累计越限 | budget cap、kill switch、max iterations | 达阈值 → 自动 pause → 人工 review |
| Over-Reach | 🔴 高 | run log 出现 denylisted path / unapproved tool call | path denylist、approval queue、escalation | 触发 denylist → escalation |
| Secrets Leakage | 🔴 高 | trace 出现 secrets pattern；audit 异常写入 | path denylist、secrets 不进 prompt/state/logs | 检测到 → immediate kill → 审计 |
| Context 串扰 | 🟡 中 | 跨 loop workspace 文件 hash 未预期变化 | per-goal worktree 隔离 + 路径限制 | 检测到 → quarantine → 人工 recovery |
| Multi-surface State Conflict | 🟡 中 | 同 `current_work_id` 多 surface 阶段不一致 | 唯一真源 = 本地 `LOOP-STATE.json`；以本地为准 | 冲突 → log alert → 人工 resolve |
| 资产下发版本漂移 | 🟡 中 | 成员资产版本 ≠ 下发版本 | git 版本锁定 + 可回滚 + SessionStart 校验 | 漂移告警 → 自动回滚或提示 |
| 文档口径分裂 | 🟡 中 | docs guardrail 测试失败 | 每次 release 运行 guardrail | 测试失败 → 禁止 release |

> 运营规则：预算 80% 切 report-only 模式；CI red / 发布期 / 关键 reviewer 不在时暂停 loop；连续 2 周 cost > value 时 kill loop；kill checklist：停 scheduler、归档 state、写 post-mortem。

---

## 14. Launch Criteria

### 14.1 v2.0 核心（团队）🆕
- MCP 默认连接器（JIRA/Plane/Confluence/GitHub）可成功双向同步。
- Agent Orchestrator 可注册并调度 claude/codex/pi 至少两类 agent 完成一个 Goal。
- 团队级 Workspace State 支持跨会话/跨成员 Handoff Packet 且可审计。
- 团队 AI 资产注册表可经 git 共享，Rules/Specs/Skills 可一键下发并回滚。
- issue-fix / pr-commit / auto-research 模板可在 quota/gate 治理下跑通至少一个真实任务并留 run log。
- checker 独立验证产生 validation receipt（checker≠maker，integrity=clean）。

### 14.2 既有基线（继承）✅
- runtime 可安装并初始化 workspace、gateway、local web control surface。
- `LOOP-STATE.json`、memory、skills、artifacts、worktree isolation 可用且可检查。
- Loop engine 支持 triage、maker/checker、run log、approvals、budget controls、stop conditions。
- Local web UI 支持 guided setup、inspection、approvals、diagnostics、export。

### 14.3 Quality and Safety
- Focused functional gate 通过：loop workspace、CLI、gateway、web UI、asset distributor。
- 每次 release 前运行 docs guardrail 测试，确认无 team-room / cloud-first / IM-first 叙事泄漏（除显式可选能力）。
- Operator 可 disable channel adapters 与资产下发，并保留完整本地 loop workspace 功能。

---

## 15. Roadmap

| 阶段 | 内容 |
| --- | --- |
| **v0.1（已实现）** | 个人循环工作区：`LOOP-STATE.json`、MCP-first、loop engine、memory、skills、artifacts、cost/safety、worktree 隔离、CLI + 本地 Web |
| **v0.2（已决策）** | 可选 IM channel adapters（DingTalk/Feishu/Slack/WeCom）、Web inspection 扩展 |
| **v1.1/v1.2（部分实现）** | handoff CLI、guided handoff、Human Model、intent/planner、trace schema、task router |
| **v2.0（本 PRD 目标）** | 团队循环工作区：MCP 系统集成（JIRA/Plane/Confluence/GitHub）、Agent Orchestrator、团队级上下文 + Handoff Packet、团队 AI 资产 git 分发、长任务模板 + quota/gate、独立验证 |
| **v2.x（增强）** | 团队额度管理（GOV-13/14）、Goal 时间线视图、Agent Work Feed、三层记忆 + Memory Dream、hash-chain 审计、GOAP plan tree、Deskop 打包、机器可读文档 |
| **v3.x（探索）** | 跨团队资产 network、模板市场、可选实时共享形态、runtime driver 抽象（含 dsh） |

---

## 16. Open Questions

- v2.0 是否需要"实时房间"作为可选形态，还是严格 local-first + git 异步共享？（当前倾向后者）
- 团队资产下发与 Proma 企业版 Skills 分发边界如何差异化（git 原生 vs Cloud 托管）？（已倾向 git 原生）
- LoopX 的 peer agent teams（claim/lease）是否引入，还是先以"多人各带 agent + 工作区共享"简化？（当前倾向后者）
- 三层记忆（person/event/experience）与 Human Model 如何合并/分层？
- 长任务模板是否开放为自定义模板市场？引入时如何避免偏离 local-first？
- 团队额度管理（GOV-13）在 v2.0 是否落地，还是仅预留接口？
- 是否将 DeepSeek Harness 作为默认 runtime driver，还是保持多 runtime 中立？

> 已决策并归档：
> - ✅ 桌面应用采用"本地 runtime + 系统 launcher"（`docs/decisions/desktop-web-im-product-boundary.md`）。
> - ✅ 内部包名迁移窗口：v1.0+ 启动（`docs/decisions/full-package-rename.md`）。
> - ✅ MCP first、ACP second；系统集成以 MCP 连接器实现。

---

## 17. 调研借鉴映射总表（Top 创新）

| LoopDesk 功能 | 来源竞品 | 实现机制要点 |
| --- | --- | --- |
| Quota + 五级 Gate | LoopX | health→operator→evidence→focus→quota 决策链 + duty cycle 记账 |
| Typed turn / typed handoff | LoopX | 执行前后枚举 + 结构化交接 |
| 公私边界 | LoopX | `public-private-boundary.md` 规范 |
| Agent Work Feed | LoopX | 推荐式卡片（产出/证据/成本/下一步/反馈） |
| Big @ / 代理借用 | Tutti | 跨代理/跨人引用 + 借用队友 agent |
| 组织级 Skills 分发 | Proma 企业版 | 一键下发、免安装、版本统一 |
| 团队额度池 | Proma 企业版 | 分配/回收/月自动/用量流水 |
| checkpoint / 时间旅行 | Octos | thread_id + committed_seq + rollback |
| swarm ledger 成本 rollup | Octos | validator gating + 幂等 ledger |
| 真源 + 派生生成 | Trellis | update 保留用户编辑 + 工作流状态机回归守护 |
| Git 即分发通道 | TeamAI CLI | MR 评审 + SessionStart 自动 pull + roles/tags/sources |
| 代码图 + BM25 重排 | TeamAI CLI | tree-sitter AST + graph-boost 检索 |
| friction 信号沉淀 | TeamAI CLI | 打断/纠正/重试触发，降噪 |
| Manager/Maker/Checker 三头分离 | LongHorizon | Manager 只读调度 + Executor fresh context + Auditor 哈希审计 |
| 主动丢弃 execution history | LongHorizon | 仅带经审计 facts 进下一轮 |
| WorkspaceSnapshot 哈希防污染 | LongHorizon | 运行前后哈希 + diff，篡改判 violation |
| 审计控制头契约 | LongHorizon | Status / Integrity / Contract audit 三行头 |
| 白盒可编辑记忆 | PilotDeck | 查/改/删/钉住决策 |
| WorkSpace 隔离 | PilotDeck / Zleap | per-project 有界文件/记忆/skills |
| `/goal` + evaluator + no-progress breaker | DeerFlow | 自动续跑 + 无进展熔断 |
| skill 包 + allowed-tools | DeerFlow | `SKILL.md` + slash 激活 + 权限约束 |
| 三层记忆 + Memory Dream | Zleap | person/event/experience + 后台经验抽取 |
| 五层安全语法 | Terax | IPC/fs/net/secret/terminal-escape 分别设防 |
| live context bridge | Terax | 持续注入 cwd/terminal/selection |
| 真实 PTY + 状态 rollup | Herdr | 不重渲染 + blocked/working/done 上卷 |
| 并行 worktree + 赢家选择 | Orca / emdash | 多 agent 隔离比较后合并 |
| hash-chain 审计 | Buzz | 每动作签名事件，篡改可检测 |
| 事件溯源 SessionEvent | DeepSeek Harness | "Model-visible means logged" |
| 机器可读文档 | Raft Docs | `/llms.txt` + `/<page>.md` |

---

## 18. Approval

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
| QA | | Pending |
