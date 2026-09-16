# LoopDesk PRD 优化建议

> 状态：Draft for review
> 版本：v1.1 → v1.2 输入
> 日期：2026-07-30
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace.md`、`docs/prd/personal-loop-workspace-v1.0.zh.md`、`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/product-positioning.md`、`docs/decisions/product-strategy.md`、`docs/decisions/desktop-web-im-product-boundary.md`、`docs/decisions/runtime-matrix.md`、`docs/decisions/v1.2-persona-workspace-boundary.md`、`docs/decisions/prd-v1.1-review-checklist.md`、`docs/features/core-feature-list.md`、`docs/architecture/personal-loop-workspace.md`、`docs/plans/prd-v1.2-gap-backlog.md`、`docs/plans/2026-07-29-loopdesk-v12-execution-plan.md`、`docs/plans/loopdesk-webui-design-spec.md`、`docs/research/loop-engineering.md`、`docs/research/competitive-intel.md` 及 `docs/research/competitive-intel-*.md` 全部竞品调研、`docs/research/prd-gap-analysis-original-vs-v1.1.md`、`docs/competition/*`
> 用途：作为 v1.1 PRD 评审与 v1.2 PRD 更新的输入建议；不替代任何已批准决策。

---

## 1. 背景与目的

本文档基于对 `docs/` 下产品设计文档（PRD v0.1 / v1.0 / v1.1、product strategy、product positioning、architecture、core feature list、desktop-web-im boundary、runtime matrix、v1.2 backlog 与执行计划、WebUI design spec）以及全部竞品调研文档（约 25 份，覆盖 Tutti、WeSight、Multica、Happier、cc-connect、Herdr、Octos、Proma、Raft、Ruflo、Orca×2、PilotDeck、Cindy、Terax、Block/Buzz、LongHorizon、LoopX、ZLeap、Bisheng、DeerFlow、EmDash、GOAI 等）的系统阅读，提炼 LoopDesk 当前设计理念，并针对产品设计文档（以 `docs/prd/personal-loop-workspace-v1.1.zh.md` 为当前权威）提出可落地的优化建议。

建议按 **P0（直接影响产品叙事与验收边界）/ P1（提升设计完整性与可执行性）/ P2（打磨与文档卫生）** 分级，每条给出：问题定位、竞品/方法论证据、建议改写、落点与验收方式。

---

## 2. 当前设计理念总结（从文档提炼）

LoopDesk 的当前设计理念可归纳为七条：

1. **Personal Agent Control Plane，不是 Agent/IDE/团队平台**：为独立开发者提供跨 Claude Code、Codex、Codebuddy、Trae、Gemini 的工具连续性，本地 workspace 是唯一 durable source of truth（`LOOP-STATE.json`）。
2. **Workspace state 是产品，不是 shell**：workspace state protocol、memory、skills、artifacts、run log、approval、budget、worktree isolation 构成产品主体；CLI + 本地 Web 网关是 v0.1 载体，桌面打包是 v1.0 分发增强，IM 是 optional continuation surface。
3. **Loop/Goal 分离 + Loop Engineering 六阶段**：Loop 后台发现与分诊，Goal 完成有界可验证任务，maker/checker 分离，run log 记录 started/acted/escalated/cost，stop condition 显式；成熟度按 L1/L2/L3 渐进。
4. **MCP-first、ACP-second 的跨工具适配层**，tool adapters 可互换，不强制 vendor shell。
5. **Local-first、portable、inspectable、安全默认**：approval、budget cap、kill switch、escalation、denylist、worktree 隔离；public exposure 需显式 opt-in。
6. **三端主次明确**：Desktop runtime（未来）最高权威 → Web 为辅（分发/setup/inspection/approval/diagnostics）→ IM 为 continuation surface（disabled-by-default）。
7. **命名纪律**：统一 LoopDesk / loop_workspace / LOOP-STATE.json / Project / Loop / Goal / Task，不暴露 legacy session / workspace-state.json / channel-first 文案。

当前实现状态：v0.1 完成（CLI + 本地 Web + loop workspace 底座）；v0.2 完成（四渠道 IM adapter）；v1.1 完成 handoff CLI、guided handoff docs、minimal human model（部分 UI 待完成）；v1.2 进行中（intent/planner、context 子结构、runtime contract、trace schema、task router，21 个测试通过）。

---

## 3. 竞品格局综合

### 3.1 竞品统一视野

| 竞品 | 核心隐喻 | 对 LoopDesk 最有价值的借鉴 | 主要冲突/风险 | 现状（调研时点） |
| --- | --- | --- | --- | --- |
| Tutti | 共享 agent workspace / cloud room | 跨 agent context handoff UX | cloud room、协作广度 | 公开 README 信号为主 |
| WeSight | desktop agent workstation | 多引擎统一 GUI、runtime 可见性 | 重 GUI shell、IM 广度 | 本地 repo + review docs |
| Multica | agent teammate 任务板 | runtime/skill/session/autopilot 模式 | team governance、issue board | 本地 repo 可查 |
| Happier | 跨设备 coding-agent 客户端 | 加密远程控制、会话延续 | bridge-first，无 durable loop state | 公开信号 |
| cc-connect | agent→IM 桥 | channel 广度、slash command 规范化 | IM-first，非 local-first loop | 公开信号 |
| Herdr | terminal agent multiplexer | 状态 rollup、detach/restore、plugin manifest | 单机 runtime 心智，无便携跨工具 handoff | 公开信号 |
| Octos | 统一本地 runtime + autonomy | goal/loop、checkpoint/resume/rewind、确定性 replay、MCP/ACP/channels、swarm 边界 | 多租户/云叙事膨胀 | 公开 repo + 代码树 |
| Proma | local-first Chat/Agent 工作台 | workspace-scoped Skills/MCP 生命周期、remote bot | desktop-shell-first，无跨工具 loop state | 公开 repo |
| Raft | 人类-AI 共享 agent workspace | onboarding-as-narrative、task handoff、Markdown/LLM-friendly docs | room-first、team-first | 公开 docs |
| Ruflo | agent meta-harness + swarm | GOAP 目标规划、plan tree、memory 持久化模式 | swarm-first、plugin sprawl | 公开 repo（活跃 v3.x） |
| Orca（×2） | parallel-worktree IDE | worktree 隔离、diff/approval UX、headless/remote host authority、usage 观测 | desktop-IDE-first，continuity 封在自家生态 | 公开 repo + docs |
| PilotDeck | agent OS / WorkSpace | 白盒可编辑记忆、成本路由、MCP 一等公民 | 重多面 agent OS | 公开 repo |
| Cindy | 多 harness workbench | 零摩擦 onboarding、harness 抽象、plugin 权限契约 | desktop/cloud/遥测默认 | 公开 repo |
| Terax | terminal-native ADE | approval-as-boundary、五层安全语法、project memory 契约 | all-in-one 范围过大 | 公开 repo + docs |
| Block/Buzz | 团队 hive mind（Nostr） | ACP/MCP 分层、hash-chain 审计、persona 模式 | team-first 社交平台，需重基础设施 | 公开 repo |
| LongHorizon-Harness | Computer-Use Agent 长程 loop | Manager/Executor/Auditor 三角色、上下文剪枝、快照哈希审计 | GUI 托管引擎，场景不同 | 公开 docs |
| LoopX | （最直接相邻竞品） | quota/gate、typed 决策词汇、Agent Work Feed | 与 LoopDesk 高度重叠 | 公开 repo（证据为自述） |
| ZLeap-Agent | 工作区隔离 + 三层记忆 agent 平台 | 工作区隔离、三层记忆（短期/长期/持久）+ Memory Dream 后台提炼 | PG 重依赖、企业向 over-delivery | 公开 repo |
| Bisheng | 企业 LLMOps 平台 | workflow/RAG/权限体系可借鉴 | 重栈、企业与 LoopDesk 定位冲突 | 公开 repo |
| DeerFlow | 全栈 super-agent harness | `/goal` + evaluator、skill 包、scheduled task MVP、observability contract | 平台化叙事需回避 | 公开 repo |
| EmDash | 并行 agent 桌面壳 | worktree-per-task UX、local-first 基线 | 单 app 会话模型埋没跨工具 handoff | 公开 repo |
| GOAI | 企业多 Agent 编排平台 | 机器可读 Validation Receipt、证据锚定 | 团队/企业叙事 + 同名 "LoopDesk" 混淆 | competition 文档 |

### 3.2 差异化空白（已验证）

**所有竞品的连续性都封在自家生态内**（Orca 在 worktree/tab、Cindy 在 app、Octos 在自己 runtime、Herdr 在自己终端、Proma 在自己工作台）。没有一家提供**跨外部工具（Claude Code ↔ Codex ↔ Trae ↔ Gemini）可导入/导出的 durable loop state**。这正是 LoopDesk 的差异化空白，建议 PRD 把"跨工具可导出 loop state"从叙事升级为可验收标准（见建议 S8）。

---

## 4. 优化建议

### A. 定位与叙事层

**S1 [P0] 竞争定位表滞后于调研语料 — 升级为三层结构 + 每竞品"不借鉴清单"。**
- 问题：PRD v1.1 §6.3 竞争定位表只列 7 个竞品（Tutti/WeSight/Multica/Happier/cc-connect/Orca/Proma）；而调研已覆盖 20+（含 Octos、Herdr、Cindy、PilotDeck、Ruflo、LoopX、Block/Buzz、Terax、LongHorizon、ZLeap、Bisheng、DeerFlow、EmDash、GOAI）。未列出的竞品中，Octos（P0 级参考）、LoopX（最直接相邻）、Cindy（零摩擦 onboarding）已被证明对设计有实质影响，PRD 不列会造成"表内竞品≠真实战场"。
- 建议：§6.3 升级为三层：直接竞品 / 相邻竞品 / 方法论参考；每行增加"借鉴什么 / 明确不借鉴什么"两列，与 §4.2 非目标形成可引用闭环。
- 落点：`docs/prd/personal-loop-workspace-v1.1.zh.md` §6.3；同步更新 `docs/product-positioning.md` 与 `docs/decisions/product-strategy.md` §4。

**S2 [P0] 产品叙事三版并存（control plane / loop workspace / personal loop workspace）— 统一为一句 elevator pitch + 30 秒 demo 脚本。**
- 问题：v1.1 用"个人 Agent 工作流控制平面"（§1），v1.0 用"个人循环工作空间"（§1），product-positioning 用"personal loop workspace"。三份权威文档口径不一，会继续向 release notes / landing page 传导（AGENTS.md 命名纪律第 6 条）。
- 建议：在 PRD 顶部固定一句话定位（建议锚定 `docs/product-positioning.md` 的 Positioning Statement），并新增"30 秒 demo 脚本"小节（安装 → 建项目 → 首个 handoff → 看到 loop state），供 onboarding/landing 复用。
- 落点：PRD §1/§6；docs/README.md 的 Read First 段。

**S3 [P0] 处理与 GOAI 方案的"LoopDesk 同名"风险。**
- 问题：`docs/competition/*` 中的企业方案也使用 "LoopDesk" 名称（多 Agent 编排 Worker Runtime），且其依赖的团队编排恰是 LoopDesk v0.1 明确延后方向。同名会造成品牌/叙事混淆，甚至误导评审与用户。
- 建议：在 PRD §4.2 非目标或 §20 风险表中显式记录该同名风险，并声明"LoopDesk 的 personal-first、local-first 控制平面定位与任何企业多 Agent 编排方案无关"。若团队决策采用其他内部代号（如 loop_workspace 产品化命名），在此记录。
- 落点：PRD §4.2 / §20；`docs/decisions/` 补一条命名/品牌决策。

### B. 领域模型与术语层

**S4 [P0] 显式定义 Task / Goal / Loop / Run 的层级与状态机，补一张领域图。**
- 问题：§7 说"新建任务 = 创建 Goal"（Task 是用户入口动作），§8.5 又把 Task 作为独立概念，v1.2 backlog B1 在补 Intent/Planner。Task 与 Goal 的关系语义未闭合，未来 planner/router 落点会摇摆。
- 建议：PRD §7 增加明确的四层模型：**Task（用户意图入口）→ Goal（执行单元，worktree 隔离 + 六阶段）→ Loop（项目内连续工作流，跨 Goal 持续）→ Run（Goal 的一次执行实例，含 trace）**；配一张状态机图（Task: open→planned→running→done/blocked；Goal: triage→maker→checker→escalation→stop）。这与 v1.2 F1（intent/planner 契约）直接衔接。
- 落点：PRD §7 + §8.5；`docs/architecture/personal-loop-workspace.md` 补领域图。

**S5 [P1] 命名纪律下沉到用户面文档 — 建立术语映射表并强制落地。**
- 问题：AGENTS.md 命名纪律只约束了核心 PRD，但 `docs/glossary.md`、`docs/use-cases.md`、`docs/web-ui.md` 等用户面文档仍在用 Session / Chat / cron 作为主词汇（glossary 将 Session 定义为"durable conversation or task history"，与 PRD 的 loop/goal/run 叙事并行）。
- 建议：在 `docs/glossary.md` 建立"遗留词 → 现行词"映射表（session→loop/goal/run、chat→task、cron→scheduler 内部能力、workspace-state.json→LOOP-STATE.json），并新增一条 docs guardrail 测试（参考已有 `tests/test_docs_guardrails.py`）检查公开文档不再以 legacy 词作为主叙事。
- 落点：`docs/glossary.md`、`docs/README.md`、`tests/test_docs_guardrails.py`。

### C. 需求与能力层

**S6 [P0] 把 v1.2 backlog 的 B1–B5 正式并入 PRD §11，避免 backlog 成为第二 PRD。**
- 问题：Intent/Planner、Context 子结构、Agent Runtime contract、Execution Trace、Task Router 已在 v1.2 实现（F1–F5），但 PRD v1.1 §11 只字未提，导致"PRD 落后于实现"。`docs/plans/prd-v1.2-gap-backlog.md` 和 `docs/plans/2026-07-29-loopdesk-v12-execution-plan.md` 事实上承担了需求定义。
- 建议：PRD 新增 §11.14 "Intent / Planner / Trace / Router Contracts（v1.2）"，逐条引用 backlog 的验收定义；PRD 成为唯一权威，backlog 只保留决策过程记录。
- 落点：PRD §11 新增小节；`docs/plans/prd-v1.2-gap-backlog.md` 更新为"已并入 PRD"。

**S7 [P1] Execution Trace / Run Log 最小字段契约写进 PRD。**
- 问题：§11.5 只有一行"记录 run log：started、found、acted、escalated、cost"；v1.2 F4 已定义 trace 字段（action、tool/runtime、duration、cost、decision、result、artifacts）与查询轴（Goal/Loop/time range）。PRD 未同步。
- 建议：§11.5 升级为"run log = structured trace，最小字段 X，查询轴 Y，replay/export 消费路径 Z"，与 v1.2 schema 对齐；这是 Success Metrics（S15）的可测量基础。
- 落点：PRD §11.5；`docs/decisions/runtime-matrix.md` 关联说明。

**S8 [P0] 新增"跨工具上下文注入契约（Context Injection Contract）" — 把 LOOP-STATE.json 的消费者视角规格化。**
- 问题：竞品证据表明 continuity 的关键不是"存了什么"，而是"下次工具启动时注入什么、以什么结构注入"：Terax 的 TERAX.md + live context bridge（持续注入 cwd/终端上下文/选区）、Raft 的 task handoff（agent 工作返回可审查结果）、Ruflo 的 plan tree。PRD 只有"inbound/outbound translation"（§11.4），没有注入载荷的最小结构。
- 建议：新增需求小节定义**跨工具 handoff 载荷**的最小结构：`project rules + 近期 decisions + active Goal（intent/criteria/stop condition）+ next action + artifact refs + cost/safety 摘要`，并声明该载荷从 `LOOP-STATE.json` + memory + skills 派生、human-readable、可 diff。这让"context re-entry"（§8 核心承诺）从口号变成可验收规格。
- 落点：PRD §11.4 扩展；`docs/architecture/personal-loop-workspace.md` 数据流图补充载荷示例。

**S9 [P1] 记忆契约（Memory Contract）— 最小条目 schema + 白盒可编辑 + compaction 规则。**
- 问题：竞品（PilotDeck 白盒记忆"可查看/可编辑/可固定决策"、Ruflo AgentDB、ZLeap 三层记忆 + Memory Dream 后台提炼、Happier E2EE、cc-connect memory instructions）均强调记忆可检查、可分层、可后台提炼；PRD §11.6 只说"durable memory + 本地搜索 + compaction"，未定义记忆条目的最小结构、分层与可编辑性。
- 建议：定义 memory 条目最小 schema（topic / fact / source（哪个 tool 哪个 run）/ confidence / updated_at / linked artifacts），支持白盒查看与编辑（仅本机），compaction/prune 规则显式，且记忆可随 partial export 跨机器迁移。与 v1.2 B2（context 子结构）合并设计。
- 落点：PRD §11.6；`docs/features/memory.md` 更新。

**S10 [P1] Runtime 能力契约（capability profile）进入 PRD §11.4，明确每个 runtime 的集成深度。**
- 问题：`docs/decisions/runtime-matrix.md` v1.2 已把矩阵升级为可校验 contract（`RuntimeCapabilityProfile`、`execute/resume/status/cancel/inspect`、默认锚点 Claude Code/Codex/Gemini），但 PRD §11.4 未引用，读者无法知道"官方支持"与"同等深度"的区别。
- 建议：PRD §11.4 引用 runtime matrix 与 capability profile，并补一张"runtime × transport × 能力深度"表（native_cli / MCP / ACP / terminal fidelity 等），声明 OpenCode 保留官方矩阵但 v1.2 不做深度适配（已决策）。
- 落点：PRD §11.4；`docs/decisions/runtime-matrix.md` 保持单一权威。

### D. 安全、成本与运营层

**S11 [P0] 风险表升级为"失败模式目录（Failure Mode Catalog）"— 每个失败模式带严重度、检测信号、缓解与 kill 规则。**
- 问题：§20 风险表只有 7 行、无检测信号与量化触发条件。loop-engineering 提供了 6 个高价值失败模式（Infinite Fix Loop、State Rot、Verifier Theater、Notification Fatigue、Token Burn、Over-Reach）及运营规则（预算 80% 切 report-only、连续失败 kill、CI red 暂停）；LongHorizon 提供 violation/integrity 门禁；Buzz 提供 hash-chain 防篡改审计。这些是 LoopDesk"loop engineering 纪律"卖点的直接证据，但 PRD 未吸收。
- 建议：§20 重构为目录式表格：| 失败模式 | 严重度 | 检测信号（run log/trace 可算） | 缓解 | kill/降级规则 |。至少覆盖：Infinite Fix Loop、State Rot、Verifier Theater、Notification Fatigue、Token Burn、Over-Reach、Secrets Leakage、Context 串扰。
- 落点：PRD §20；`docs/research/loop-engineering.md` §5 作为来源；`docs/decisions/risk-handling-plan.md` 同步。

**S12 [P1] maker/checker 强化为"独立验证"语义：checker 必须 fresh context / 只读 / 快照哈希，并明确"implementer 不能给自己打分"。**
- 问题：PRD §11.5 只说"maker/checker split"。LongHorizon 的三角色（Manager read-only / Executor fresh-context / Auditor 只读 + WorkspaceSnapshot 哈希）、loop-engineering 的"implementer 不能给自己打分"、DeerFlow 的 `/goal` + evaluator、GOAI 的"Validation Receipt"都指向 checker 必须独立于 maker 的上下文与权限。
- 建议：在 §11.5 明确：checker 以 fresh context 运行、只读（或 worktree 内）、可对 workspace 快照做哈希校验；Goal 完成产生机器可读的验证凭证（validation receipt：criteria、evidence refs、checker run id），回写 run log 与 artifact。
- 落点：PRD §11.5；v1.2 F4 trace schema 增加 verification receipt 字段。

**S13 [P1] 上下文剪枝规则：每轮执行后只把验证过的产物/状态带入下一轮。**
- 问题：LongHorizon 的核心机制是"executor 原始历史彻底剪枝、只把 verified facts/artifacts 带到下一轮"；loop-engineering 是"每次 run 读取 prior state、写 outcome、prune closed items"。PRD 的 compaction（§11.6）只针对长 session，未覆盖"跨 Goal/跨 run 的意图级剪枝"。
- 建议：§11.6 增加一条：每个 Goal run 结束后，将未验证的中间过程从连续上下文移除，只保留 verified facts、decisions、artifacts 与 next action 进入下一 run；与 S8 注入契约联动。
- 落点：PRD §11.6 + §7 Goal 生命周期。

**S14 [P2] 防篡改 run log（hash-chain）作为 P2 增强。**
- 问题：Buzz 的 hash-chain 审计（每个动作是签名事件）与 LongHorizon 的快照哈希验证证明"审计完整性"对信任型产品有价值；PRD 目前无此要求。
- 建议：作为 P2 列入 §11.5 run log 的 future 增强（worktree 快照哈希 + run log 链式摘要），不阻塞 v1.2。
- 落点：PRD §11.5 备注；`docs/plans/prd-v1.2-gap-backlog.md` 新增 backlog item。

### E. 用户体验与场景层

**S15 [P0] Success Metrics 可操作化：每个指标给出定义、测量点、基线、目标与验证实验。**
- 问题：§17 有 8 个指标（context re-entry time、loop completion rate、cross-tool fidelity、surface adoption、cost predictability、remote approval latency、recovery success、onboarding completion），但绝大多数没有测量方法：context re-entry time 怎么测？cross-tool fidelity 百分比从哪来？对 local-first 无云产品，必须能从本地 run log/trace 直接计算，否则指标永远无法验证。DeerFlow 的 observability contract（structured run 数据作为一等公民）证明这是可实现的，而非口号。
- 建议：为每个指标补一行"测量定义"：数据源（structured trace / run log / opt-in 本地埋点）、计算公式、基线（v1.1 实测或估计）、目标值（如 loop completion rate ≥ 80%、handoff fidelity = 满足注入契约的 handoff 比例 ≥ 90%）。onboarding completion（首次 setup 完成 project/loop/resume）作为 v1.0 primary metric 已在 §17 出现，需补阈值。
- 落点：PRD §17；`docs/acceptance/` 增加指标测量说明。

**S16 [P0] Onboarding-as-narrative：定义"首次运行 5 分钟内完成首个有用 loop"的验收语言。**
- 问题：Raft（onboarding agent 引导首个真实任务）、Cindy（零摩擦：隐藏 key/CLI/MCP 复杂度、自动发现与 fallback）、Orca（免登录、自带订阅即用）都证明 onboarding 决定产品第一印象；PRD §9.3 guided setup 与 §18.1 有 handoff docs 要求，但没有"从安装到首个有用 loop"的具体流程与时间目标。
- 建议：§9.3 补一段 onboarding narrative：安装 → `loopdesk onboard` → 建项目 → 连首个工具（自动发现本地 Claude Code/Codex）→ 创建首个任务 → 看到 loop state + next action；并设置验收语言"5 分钟内跑通、无关键术语障碍"。复用 `docs/plans/loopdesk-webui-design-spec.md` 的 guided setup 角色。
- 落点：PRD §9.3 / §18.1；`docs/guides/guided-handoff.md` 对齐。

**S17 [P1] WebUI 与 PRD 互引，清理 legacy web-ui.md 口径。**
- 问题：`docs/plans/loopdesk-webui-design-spec.md` 已定义完整的项目视图/工作台/新建任务规格，但 PRD §13 未引用它；同时 `docs/web-ui.md` 仍描述 legacy 多渠道 console（spec §10 open item 已指出，未关闭）。
- 建议：PRD §13 增加"Web 规格锚点：`docs/plans/loopdesk-webui-design-spec.md`"；将 `docs/web-ui.md` 标记 legacy 或按 spec 重写。
- 落点：PRD §13；`docs/web-ui.md`；`docs/README.md` 索引。

**S18 [P2] Goal 生命周期时间线视图（Plan→Execute→Audit→Decision 卡片流）作为 WebUI follow-up。**
- 问题：LongHorizon 的卡片瀑布流、Octos 的 checkpoint/resume、EmDash 的 worktree-per-task UX 都证明"Goal 的历史进程可视化"比"当前状态摘要"更有说服力；PRD §13.3 inspection 只列了"active runs/pending approvals/recent artifacts"。
- 建议：在 WebUI design spec 的 follow-up 增加"Goal 时间线视图"（六阶段 stepper + 每阶段 trace 事件 + resume/rewind 入口），列为 v1.2/v1.3 Web 增强。
- 落点：`docs/plans/loopdesk-webui-design-spec.md` §10。

### F. 指标、验收与范围护栏

**S19 [P1] Launch Criteria 与验收测试建立映射（每个 criterion 指向证据位置）。**
- 问题：PRD §18 的 launch criteria 与 `docs/acceptance/` 的 checklist 各自成文，无显式映射；v1.2 execution plan 已有 gate 命令（21 tests），可作为模板。
- 建议：§18 每行增加"证据"列（对应 acceptance checklist 文件 + 测试命令 + 文档位置），让评审可以逐条核验。
- 落点：PRD §18；`docs/acceptance/loopdesk-v1.1-acceptance-checklist.md`。

**S20 [P1] anti-scope guardrail 升级为强制 release 检查。**
- 问题：现有 anti-room guardrail（🔲 v1.0）与 docs guardrail 测试（`tests/test_docs_guardrails.py`）已存在，但 PRD 未把它们写成"每次 release 必须通过"的验收项。
- 建议：§18.5 增加强制项：每次 release 前运行 docs guardrail 测试，确认无 team-room / cloud-first / IM-first 叙事泄漏；把"不借鉴清单"（S1 的产出）也纳入检查。
- 落点：PRD §18.5；`tests/test_docs_guardrails.py` 扩展。

**S21 [P2] 明确"不采纳清单" — 把竞品分析结论固化为范围护栏。**
- 问题：调研反复强调"不复制 Octos 多租户、不复制 Buzz 社交平台、不复制 Terax all-in-one、不复制 LongHorizon GUI 托管、不复制 Ruflo swarm-first、不复制 Cindy 云后端、不复制 Bisheng 企业 LLMOps 重栈、不复制 ZLeap 企业向 over-delivery、不复制 EmDash 单 app 会话模型（埋没跨工具 handoff）、不复制 GOAI 企业编排"，但 PRD §4.2 只写抽象的非目标，没有可引用的具体条目。
- 建议：PRD §4.2 增加"明确不采纳"小节，逐条列出上述竞品形态 + 一句理由 + 引用调研文档，使范围决策可审计。
- 落点：PRD §4.2；`docs/research/competitive-intel.md` §4.3 作为来源。

### G. 文档工程与卫生

**S22 [P1] 修复 PRD v1.1 自身的一致性问题。**
- 问题：
  1. §21 Open Questions 存在重复（Electron/loopdesk 包名迁移问题出现两次，一次标注 ✅ 已确认、一次标注 🔲 留 v1.0+，自相矛盾）；
  2. v1.0 与 v1.1 内容高度重叠（v1.1 是 v1.0 的近复制 + control-plane 强化），`docs/README.md` 同时把 v1.0 与 v1.1 列为权威 PRD 锚点（desktop-web-im 决策 §9 说"以 v1.0 zh/en 为正式 PRD"，README 又列 v1.1），存在双 PRD 漂移；
  3. 完成度图例 ✅/🔲/⏳ 无法区分"已实现未验证"与"已决策未实现"。
- 建议：v1.1 的 Open Questions 去重并只保留仍未决策项；明确"v1.0 → v1.1 → v1.2"的演进关系（建议在 PRD 头部加版本史表：日期、变化、权威状态），README 只指向当前权威版本；完成度图例增加第四种状态（如 🔶 = 已实现、待验收）。
- 落点：`docs/prd/personal-loop-workspace-v1.1.zh.md` §21/头部；`docs/README.md`。

**S23 [P2] 竞品调研索引化 + 同产品二次调研去重。**
- 问题：20+ 份 competitive-intel-*.md 散落在 `docs/research/`，无统一索引（`docs/README.md` 只列了少数）；Orca 存在两次独立调研（`competitive-intel-stablyai-orca.md` 与 `competitive-intel-yasinkavakli-orca.md`，同一产品、口径可能漂移）。
- 建议：`docs/research/README.md` 或 `docs/README.md` 增加"竞品调研索引"表（竞品 → 文件 → 一句话结论 → 借鉴/不借鉴锚点）；两份 Orca 调研合并或互引（stablyai 为主，yasinkavakli 标注为同产品早期取证）。
- 落点：`docs/README.md`；`docs/research/competitive-intel-yasinkavakli-orca.md` 头部加互引说明。

---

## 5. 与现有文档/backlog 的衔接

| 本文建议 | 承接方 | 现有锚点 |
| --- | --- | --- |
| S4（领域模型） | PRD §7 + 架构图 | `docs/plans/prd-v1.2-gap-backlog.md` B1 |
| S6（B1–B5 并入 PRD） | PRD §11 新增小节 | `docs/plans/2026-07-29-loopdesk-v12-execution-plan.md` F1–F5 |
| S7（trace schema） | PRD §11.5 | v1.2 F4 |
| S9（记忆契约） | PRD §11.6 | v1.2 B2（context 子结构） |
| S10（runtime contract） | PRD §11.4 | `docs/decisions/runtime-matrix.md` v1.2 补充决策 |
| S11（失败模式目录） | PRD §20 | `docs/decisions/risk-handling-plan.md` |
| S12（独立验证凭证） | PRD §11.5 + F4 trace | LongHorizon / GOAI 调研 |
| S15（指标可操作化） | PRD §17 | `docs/acceptance/` |
| S17（WebUI 互引） | PRD §13 | `docs/plans/loopdesk-webui-design-spec.md` |
| S20（guardrail 强制） | PRD §18.5 | `tests/test_docs_guardrails.py` |
| S22（版本史/去重） | PRD 头部 + §21 | `docs/README.md` |

## 6. 建议的后续动作

1. 在 v1.1 评审会议中逐条过 S1–S3、S4、S6、S8、S11、S15、S16（P0 组），拍板后回填 PRD v1.1 或直接进入 v1.2 PRD 更新。
2. 将 P1 组（S5、S7、S9、S10、S12、S13、S17、S19、S20、S22）纳入 v1.2 backlog 的 grooming，与 B1–B5 合并排期。
3. 将 P2 组（S14、S18、S21、S23）作为 optional enhancement，进入 `docs/plans/prd-v1.2-gap-backlog.md`。
4. 本文件评审通过后，在 `docs/README.md` 建立竞品调研索引并链接本文件。
