# PRD — LoopDesk 个人循环工作空间

> 状态：v1.0 重写稿（评审中）
> 版本：v1.0
> 负责人：Product / Engineering
> 最后更新：2026-07-17
> 输入：`docs/decisions/product-strategy.md`、`docs/decisions/desktop-web-im-product-boundary.md`、`docs/decisions/module-audit-loopdesk-vs-loopdesk.md`、`docs/decisions/raft-borrow-patterns.md`、`docs/architecture/personal-loop-workspace.md`、`docs/research/competitive-intel.md`、`docs/features/core-feature-list.md`、`docs/releases/loopdesk-v0.1.md`、`docs/releases/loopdesk-v0.2.md`、`docs/decisions/v0.2-channel-adapter.md`

> **完成度图例**
> - ✅ = v0.1 已实现
> - 🔲 = 已设计 / 已决策，实现待排期（多落在 v0.2 或 v1.0）
> - ⏳ = v0.2 范围（已决策，实现待排期）

---

## 1. 目标

本文档定义 LoopDesk 的完整产品方向：一个 **local-first 的个人循环工作空间**，以 **CLI + 本地 Web 网关**为当前实现载体，以 **桌面应用打包**为未来分发目标，并以 **IM 为可选远程继续面**，用于在受控前提下从聊天工作区继续已批准的工作。

LoopDesk 帮助独立开发者把 Claude Code、Codex、Codebuddy、Trae、Gemini 及类似工具之间的上下文、记忆、循环状态和执行过程连贯起来。本地 workspace 是唯一 durable source of truth。

> 定位说明：当前 v0.1 的交付物是 **CLI（`loopdesk`）+ 本地 Web UI（网关）**。PRD 中"桌面应用"指未来的原生打包目标（v1.0 方向），不是 v0.1 的现实。详见 §3、§9、§12、§16。

## 2. 背景

独立开发者经常在多个 coding agent、终端和工具之间切换。当前竞品大多只能解决其中一部分问题：
- Tutti 偏向共享上下文 handoff，但 durable portable state 不够强；
- WeSight/Orca 偏向本地 runtime 可见性和桌面 GUI，但容易变成重 shell；
- Happier/cc-connect 偏向远程控制与 channel breadth，但没有把 loop engineering 和本地状态所有权放到核心；
- Proma 偏向本地 Chat + Agent 桌面工作台、Skills/MCP 与 remote bot 体验，但更偏向"自己的桌面工作流 shell"，而不是跨工具的 durable loop continuity。

LoopDesk 应该占据的 niche 是：一个 **portable personal loop workspace**，让开发者的下一步动作、已有决策和当前执行状态可跨工具查看和继续，同时不强制绑定某个 vendor shell、cloud room 或 SaaS runtime。

## 3. 技术遗产声明：LoopDesk 作为"血包"

LoopDesk v1.0 在代码层面建在 OpenSquilla 运行时之上，但二者在产品上无关：

- **OpenSquilla 是"血包"（功能模块供应源），不是产品本身。** LoopDesk 需要哪块能力，就直接从血包抽取对应模块，本身与 LoopDesk 品牌/叙事无关。
- **真正值得抽取的两块器官**：
  1. **Skill 管理**（`skills/`）：可复用技能与元技能运行时，是 LoopDesk 的核心能力来源。
  2. **IM 相关功能**（`channels/`）：作为 v0.2 渠道适配器的实现基础；v0.1 不暴露 IM 用户面。
- **其余底层 / 网关层不计为 LoopDesk 价值**：`engine/`、`gateway/`、`cli/`、`tools/`、`memory/`、`provider/`、`mcp/`、`mcp_server/`、`safety/`、`sandbox/`、`session/`、`dist/`、`agents/`、`identity/`、`chat/` 一律视为 **OpenSquilla 自有运行时**，其 LoopDesk 出处不在产品叙事中出现。
- **命名策略**：v0.1 公开面（二进制名、环境变量、配置文件、`clientInfo`、类名、文档）全部使用 `loopdesk`；内部 Python 导入路径暂留 `loopdesk`，v0.2+ 再做全量包名迁移。
- 模块级 Cancel / Retain / Core 分类与"血包抽取"映射见 `docs/decisions/module-audit-loopdesk-vs-loopdesk.md`。

## 4. 目标与非目标

### 4.1 目标
- 降低跨工具切换时的上下文重入成本。
- 提供 durable workspace，承载任务、记忆、skills、artifacts、loop state 与 worktree isolation。
- 以 **CLI + 本地 Web 网关**为 v0.1 主载体；以 **原生桌面打包**为未来分发增强目标。
- 以 Web 为分发、guided setup、workspace inspection、approval、diagnostics surface。
- 以 IM 为 continuation surface：选择 workspace、查看状态、approve/reject、继续已批准的 bounded work。
- 支持 loop-driven automation，并内置 safety、cost control、local observability 与 explicit stop conditions。
- 保持 personal、local-first、portable、inspectable。

### 4.2 非目标
- 不做通用 team collaboration suite。
- 不替代 Claude Code、Codex、Codebuddy、Trae、Gemini。
- 不让 IM 成为主 runtime 或主叙事。
- 不强制 cloud sync、cloud rooms、multi-user workspaces。
- 不做 heavy IDE 或 broad creator/media/team 功能堆料。

## 5. 目标用户

### 5.1 主要用户
- 独立开发者：独自或只使用少量 AI 工具完成编码、文档、review 和发布。

### 5.2 次要用户
- Operator-developer：希望在另一台设备上查看运行状态、approve/reject 和 triage alerts，而不一定回到桌面。
- Power user：希望在已批准且 bounded 的工作项上做跨设备继续。

### 5.3 用户诉求
- 在一台机器上启动工作，在本地 Web 或可信 remote surface 上继续。
- 从 IM 选择 workspace 并继续已批准任务，而不用重新解释完整上下文。
- 在一个地方查看 loop state、run log、memory、skills、approvals 和 cost。
- 在没有 proprietary cloud lock-in 的前提下保持工作可移植、可恢复。
- 用 worktree isolation、approval、kill condition 安全运行高风险或重复性 loops。

## 6. 产品叙事

### 6.1 产品承诺
- 在任意支持的 coding agent 中启动任务；
- 不复制粘贴完整上下文，即可从 CLI、local web、或 approved IM workspace 继续；
- 看到当前 loop state，而不是只看到最新一条 chat message；
- 让 LoopDesk 建议下一个 safe action、展示 cost，并记录 outcome；
- 把 decisions、artifacts、run history 保存在一个可搜索的个人 workspace。

### 6.2 定位声明
对于在 Claude Code、Codex、Codebuddy、Trae、Gemini 和本地终端之间切换的独立开发者，LoopDesk 是一个 **local-first personal loop workspace**，在工具之间统一上下文、记忆、loop control 与连续工作流。与 Orca 相比，它不会变成另一个重 agent IDE；与 Happier 相比，它不会优先做 encrypted remote mirroring 而忽略 durable loop state；与 cc-connect 相比，它不会把 IM 当主产品；与 Proma 相比，它不会变成某个桌面 Chat/Agent shell 的内部工作流，而是做跨工具的 durable cross-tool loop continuity layer。

### 6.3 竞争定位

| 竞品 | 优势 | 过度交付 | LoopDesk 可借力缺口 |
| --- | --- | --- | --- |
| `tutti-os/tutti` | 共享 agent workspace、cross-agent handoff | cloud rooms、collaboration breadth | solo local-first minimal loop |
| `freestylefly/wesight` | desktop runtime visibility、multi-engine GUI | GUI shell breadth、IM breadth | lightweight context layer |
| `multica-ai/multica` | team task management、runtime daemon、autopilot | team governance、issue board、cloud sharing | personal loop state and continuity |
| `happier-dev/happier` | cross-device session control、E2EE、multi-provider | remote-control/bridge-first product | durable loop-state platform with loop engineering |
| `chenhg5/cc-connect` | channel breadth、zero-public-IP transports、slash commands | IM-first chat bridge | local-first loop execution and durable `LOOP-STATE.json` |
| `stablyai/orca` | parallel worktrees、rich terminal UX、diff/PR/Linear review | IDE-shell-first product | portable cross-tool context handoff and loop engineering |
| `proma-ai/proma` | local-first Chat/Agent workbench、Skills/MCP、remote bot bridges | desktop-shell-first Chat/Agent workflow | durable cross-tool loop state and cross-tool continuity |

### 6.4 战略差异点
- **Local-first runtime**：安装、gateway、文件访问、agent orchestration、inspection 都以本地为主。
- **Web 为辅**：用于分发、setup、inspection、approval、diagnostics，不替代本地 runtime。
- **IM 为 continuation surface**：用于选择 workspace、查看状态、approve/reject、继续已批准 bounded work，不跑完整 loop。
- **Context continuity first**：workspace state 是产品，不是 shell。
- **Tool-agnostic loop**：MCP-first、ACP-second、不强制 vendor UI。
- **Loop engineering discipline**：triage、maker/checker、run log、budget、escalation、stop condition 是 first-class behavior。
- **Local control and portability**：local-first runtime、inspectable state files、export/import、无强制 cloud account。

## 7. 核心概念模型：项目 / 循环 / 目标 / 任务

本节定义 LoopDesk 的领域模型（设计已锁定，部分实现待排期）。

```
项目 Project（顶层空间，侧栏 项目切换器）
└─ 循环 Loop（1 项目 = 多 Loop，各自独立连续工作流；侧栏 Loop 切换器）
   └─ 目标 Goal（每 Loop 多个；各享 worktree 隔离 + Loop Engineering 六阶段）
      ↑ 新建任务 = 创建一个 Goal，自动进入当前活跃 Loop
```

- **项目 Project** ✅🔲：顶层空间容器，承载独立上下文、状态与交付物。侧栏 项目切换器 选择；任务必须归属某个项目，未显式选择时默认当前项目。
- **循环 Loop** 🔲：每个项目下可有多个独立 Loop（不同工作流 / 代理 / 上下文）。侧栏 Loop 切换器 选择当前查看的 Loop。Loop 是项目内的"连续工作流"，跨多个 Goal 持续运行，持有项目的连续上下文（memory / artifacts / run log）。
- **目标 Goal** ✅🔲：Loop 内的具体工作单元，每个 Goal 享一个 worktree 隔离，并走 Loop Engineering 六阶段（分诊 → 制作 → 检查 → 升级 → 运行日志 → 停止）。
- **任务 Task（新建任务）** 🔲：用户侧"新建任务"动作即创建一个 Goal。必须归属项目（必选，缺省默认当前）→ 同时归属 Loop（必选，缺省默认当前活跃 Loop）。新建任务自动进入当前活跃 Loop，需要时再在 Loop 间移动。
- **Workspace 视图** ✅：= 当前 Loop 的连续工作视图（Loop 隐式贯穿，无独立 Loop 页）。Current work = 活跃 Goal 的阶段进度；Observatory = 该 Loop 指标；状态 chips = 该 Loop 聚合；继续工作 = resume 活跃 Goal 的 loop。
- **交付物** ✅🔲：随 Goal 沉淀到项目上下文（spec / test / PR 等），不随会话丢失。

> 命名纪律：统一使用 LoopDesk / loop_workspace / LOOP-STATE.json / Project / Loop / Goal / Task，不暴露 OpenSquilla 遗留的 session / workspace-state.json / channel-first 文案。

## 8. 用户体验

### 8.1 主流程 ✅🔲
1. 开发者安装 CLI 或 runtime，并在 setup 过程中明确下一步动作：创建项目、选择 Loop、绑定 worktree，或 resume 现有 Goal，避免一上来就暴露完整工具矩阵；🔲 v1.0 guided handoff
2. 初始化本地 loop workspace、`LOOP-STATE.json`、memory、skills、artifacts、worktree；🔲 项目 / 多 Loop 初始化
3. 通过 MCP-first、ACP-second 或 tool-specific adapters 连接工具；✅
4. LoopDesk 判断当前工作应继续 discovery、triage、synthesis，还是收敛成 bounded Goal；✅
5. 开发者从 CLI 或 local web UI 查看 state；敏感动作需要 explicit approval；✅
6. 离开主环境时，可通过 web 或 IM 查看状态、approve/reject、继续 approved bounded work；🔲 web ⏳ IM
7. 结果、decisions、run history 回写本地 workspace；✅
8. 开发者从 durable workspace state 切换到其他工具，无需重新粘贴上下文。✅

### 8.2 Local-first 原则
- 本地 runtime 拥有 gateway lifecycle、本地文件访问、agent process、worktree isolation 的最高权威。✅
- CLI + local web UI 是当前最丰富的 inspection surface：run log、approval queue、cost、memory、skills、artifacts、diagnostics。✅
- Web 是本地 workspace 的功能延伸，不是完整本地 runtime 的独立复刻。✅
- IM 是 intentionally minimal：选 workspace、看状态、继续 approved work、approve/reject、收 compact notification。⏳

### 8.3 Web 原则 ✅
- Web 是首选 onboarding 和 distribution 路径。
- Web setup 应提供"当前任务 handoff 视图"：project 归属、活跃 Loop、next safe action、resume path，而不是仅展示 runtime 能力清单；🔲 v1.0 guided handoff
- Web inspection 应展示 loop state、active runs、pending approvals、recent artifacts、channel status。
- Web control 应支持 bounded safe actions：read-only inspection、continue approved bounded work、submit approval decisions、view run log、export workspace state。
- Web 不应以牺牲本地 runtime fidelity 为代价去复刻完整本地文件编辑或终端 orchestration。

### 8.4 IM 远程控制原则 ⏳
- IM 默认关闭。
- IM 命令映射到现有 safe workspace actions；不引入新 shell、team-room 或 chat-first workflow semantics。
- 第一个 IM 动作通常是 workspace selection 或 status inspection，而不是 unbounded execution。
- Long-running / high-risk work 继续由本地 runtime 拥有；IM 仅用于 continuation、notification、lightweight steering。

### 8.5 Loop/Goal → UX 桥接（后端模型与前端交互）🔲
本节把后端概念与前端交互显式对应，闭合"用户如何看到并操作 Loop/Goal"的问题。

**后端业务模型**
- Project 持有独立上下文；Loop 是项目内连续工作流；Goal 是 Loop 内的 bounded 工作单元。
- 每个 Goal 享一个 worktree（OS 级沙箱 + 路径限制 + 审计快照），保证跨 Goal 不串扰。
- Loop Engineering 六阶段是 Goal 的生命周期状态机；Run Log 记录每个 Goal 的 started / acted / escalated / cost / outcome。

**前端交互映射**

| 后端概念 | 前端落点 | 交互行为 |
| --- | --- | --- |
| Project | 侧栏 项目切换器 | 切换即切换上下文、状态、交付物 |
| Loop | 侧栏 Loop 切换器（项目切换器下方） | 切换即切换当前 Workspace 渲染的 Loop |
| Goal | Workspace 的 Current work 面板 + 新建任务 | 新建任务 = 在当前 Loop 建 Goal，进入分诊 |
| 六阶段状态 | Current work 内的阶段 stepper | 已完成=绿、进行中=teal 高亮、未开始=灰 |
| Loop 指标 | Observatory 面板 + 状态 chips | 花费/预算/安全/待审批 等 Loop 级聚合 |
| 交付物 | 项目上下文 + Run Log | 随 Goal 沉淀，不随会话丢失 |
| Resume | 状态条"继续工作"按钮 | resume 当前/最近活跃 Goal 的 loop |

**关键交互规则**
- 新建任务：在当前活跃 Loop 创建 Goal；项目/ Loop 未选择时分别默认当前项目 / 当前活跃 Loop。
- 多 Loop：Workspace 跟随侧栏 Loop 切换器；无独立 Loop 页（Loop 隐式贯穿）。
- 人工介入点：只在 approval、escalation、ambiguity、high-risk action、insufficient authorization 时暂停。

## 9. 场景

### 9.1 安装并初始化 runtime ✅🔲
- 开发者安装 CLI（未来：下载 macOS / Windows / Linux 桌面包）；
- runtime 初始化本地 gateway、workspace directory 和 `LOOP-STATE.json`；
- 在 CLI 或 bundled local web setup surface 配置 providers、MCP/ACP adapters、first project。🔲 多项目 / 多 Loop 初始化

### 9.2 CLI + 本地 Web 作为主控制面 ✅
- 开发者运行 loop workspace（CLI + local web UI）；
- 暴露 loop state、run log、memory、skills、artifacts、approvals、cost、diagnostics；
- 通过 shared workspace state 在 coding agents 之间切换，而非手动复制上下文。

### 9.3 Web 分发与 guided setup ✅
- 开发者打开官网 / download / setup 页面；
- Web 引导 provider auth、workspace template、MCP/ACP adapter onboarding、safety defaults；🔲 channel enablement 留 v0.2
- Setup 完成后，web 变成 inspection 和 approval companion，不是主 execution runtime。

### 9.4 Web inspection 与 operator control ✅
- 开发者打开 local web UI，查看 active runs、approvals、cost；
- Operator 可查看 run log detail、replay packs、memory updates；
- 敏感动作保持 approval-gated，并记录在本地 workspace state。

### 9.5 从 Web 远程继续 ✅🔲
- 开发者离开主环境，但仍需继续 approved bounded task；
- Web surface 显示当前 workspace、selected in-flight Goal、recent artifacts、next safe actions；
- 开发者可发送 follow-up guidance、approve next step、reject risky branch；resume 后执行仍在本地发生。

### 9.6 IM workspace 选择与状态 ⏳
- 开发者打开 approved IM channel 并选择 LoopDesk workspace；
- IM surface 显示当前 loop status、pending approvals、cost alerts、short run summary；
- 开发者可以看到本地 runtime 是 active、idle，还是 waiting for input。

### 9.7 IM remote approval 与 follow-up ⏳
- LoopDesk 向 IM 发送 compact approval request 或 cost alert；
- 开发者从 IM approve/reject，结果回写本地 run log 和 approval history；
- 开发者对 in-flight approved task 发送 short follow-up；runtime 在 active 时处理，否则排队到下一个 safe execution window。

### 9.8 跨工具 continuity ✅
- 在 Claude Code 中启动，在 Codex 或 Trae 中继续，在 CLI / local web UI 中查看 state；
- Context handoff 由 `LOOP-STATE.json`、memory、skills、artifacts 驱动；
- IM 仅用于 lightweight continuation；authoritative state 始终留在本地 workspace。

## 10. 范围

### 10.1 在范围内
- ✅ Local-first runtime：gateway、workspace state、loop engine、adapters、memory、skills、artifacts、worktree isolation。
- 🔲 项目 / 多 Loop 模型与切换器（CLI + Web UI）。
- ✅ CLI（`loopdesk`）+ local web UI：guided setup、workspace inspection、approval、diagnostics、replay、distribution。
- 🔲 原生桌面应用打包（macOS / Windows / Linux），作为 v1.0 分发增强。
- ⏳ Optional IM adapters：DingTalk、Feishu/Lark、Slack、WeCom，作为 lightweight remote control / notification surface（v0.2）。
- ✅ 本地优先数据所有权：export/import、backup、audit trail。
- ✅ v0.1 作为 stable baseline；⏳ v0.2 渠道适配器作为已决策扩展。

### 10.2 不在范围内
- Multi-user collaboration、shared cloud rooms、team workspaces、roles、enterprise onboarding 作为核心需求。
- Heavy desktop GUI IDE shell 作为主要差异化（桌面打包仅作分发目标，不堆料）。
- IM-first narrative、rich media pipeline、voice replies、complex card interactions、chat-first loop execution。
- Mandatory cloud sync、cloud-hosted workspace state、SaaS accounts for core workflow。
- Personal WeChat、QQ、Telegram、Discord、Matrix 等 v0.2 approved set 之外的额外平台。

## 11. 需求

### 11.1 Runtime（CLI + 本地网关）✅
- runtime MUST 初始化并管理本地 gateway 与 workspace directory。
- runtime MUST 暴露 loop state、run log、approvals、memory、skills、artifacts、cost、diagnostics。
- runtime MUST 支持本地文件访问、worktree creation、agent lifecycle、restart/recovery。
- runtime 除 optional IM transports 和 provider API 外，core workflow 应支持 offline。

### 11.2 Workspace State Protocol ✅
- 系统 MUST 维护 `LOOP-STATE.json` 作为 portable source of truth。
- 系统 MUST 把 memory、skills、artifacts、worktrees 放在同一 workspace boundary。
- 系统 MUST 支持 export/import，且不强制 cloud account。

### 11.3 项目与多 Loop 模型 🔲
- 系统 MUST 支持项目（Project）作为顶层空间容器，承载独立上下文、状态、交付物。
- 系统 MUST 支持每个项目下多个独立 Loop，各自持有连续上下文。
- 系统 MUST 提供项目切换器与 Loop 切换器，切换即切换 Workspace 渲染的上下文。
- 新建任务 MUST 归属项目（必选，缺省默认当前），并归属 Loop（必选，缺省默认当前活跃 Loop）。

### 11.4 Cross-Tool Integration ✅
- 系统 MUST 支持 MCP-first integration。
- 系统 SHOULD 支持 ACP-second integration。
- 系统 MUST 把 inbound tool events 翻译成 workspace state，并把 workspace state 翻译成 tool-ready input。
- Tool adapters MUST 可互换，不强制单一 agent shell。

### 11.5 Loop Engine ✅
- 系统 MUST 支持 scheduled、fire-immediate、durable、controllable loops。
- 系统 MUST 实现 triage、maker、checker、escalation。
- 系统 MUST 记录 run log：started、found、acted、escalated、cost。
- 系统 MUST enforcing stop conditions 与 completion criteria。
- CLI / Web / IM MUST 反映同一 backend loop/goal state。

### 11.6 Memory and Context Continuity ✅
- 系统 MUST 提供 durable personal memory 与本地搜索。
- 系统 MUST 支持 loop/goal run continuity：compact、cache continuity、resume、history、export、replay、abort。
- 系统 MUST 支持把 completed goal 知识 flush 进 memory。
- 命名约束：不暴露 OpenSquilla 遗留的 session 文案；连续状态统一以 loop / goal / run 表达。

### 11.7 Skills ✅（来自 LoopDesk 血包：Skill 管理）
- 系统 MUST 支持 reusable skills 和 meta-skills（源自 LoopDesk `skills/` 模块）。
- 系统 MUST 支持 inspection、replay、audit。
- 系统 SHOULD 支持基于 task context 的 skill auto-triggering。
- LoopDesk 的 Skills 绑定 cross-tool loop context，而不是仅服务于单个客户端内部 workflow。

### 11.8 MCP 与可借鉴扩展 ✅
- 系统 MUST 支持 stdio / HTTP MCP server。
- 系统 SHOULD 支持 per-workspace MCP configuration 与 enable/disable 生命周期。
- MCP 需与 `LOOP-STATE.json`、loop engine、approval、budget、run log 联动，并支持跨 tool adapter 的上下文注入与回写。

### 11.9 Runtime Visibility and Control ✅
- 系统 MUST 提供本地 inspection：active runs、approvals、logs、errors、memory、skills、worktrees。
- 系统 MUST 提供 local web UI：guided setup、inspection、approval、diagnostics。
- Web MUST 保持 secondary，且不得替代本地 gateway authority。

### 11.10 IM Remote Control ⏳
- IM adapters MUST disabled-by-default。
- IM 默认只读 inspection；write actions 需要 explicit enablement、allowlist、approval-gating。
- IM MUST 支持 workspace selection、status、compact run summaries、approve/reject、bounded follow-up。
- IM MUST NOT 引入 team-room semantics、chat-first loop execution、unbounded shell access。
- IM 能力源自 LoopDesk `channels/` 模块（v0.2 渠道适配器基础），v0.1 不暴露。

### 11.11 Safety and Cost ✅
- 系统 MUST 跟踪 token 和 cost。
- 系统 MUST enforcing budget caps、daily limits、max iterations、kill switches。
- 系统 MUST 提供 approval queue。
- 系统 MUST 支持 escalation：ambiguity、repeated failure、denylisted paths。
- CLI / Web / IM 的 approval action MUST 记录在同一 local audit trail。

### 11.12 Isolation ✅
- 系统 MUST 支持 per-goal worktree 或 scratch directory。
- 系统 MUST 支持 cleanup 或 retained audit snapshots。
- 系统 MUST 避免 cross-loop workspace corruption。
- Remote surfaces MUST NOT bypass worktree isolation 或 local safety controls。

### 11.13 Distribution and Deployment 🔲
- ✅ CLI + web-guided install 为当前主路径。
- 🔲 原生桌面 installers/packages（macOS / Windows / Linux）为 v1.0 打包目标。
- 系统 MUST 在 upgrade/rollback 时保留本地 workspace data。
- 默认 gateway binding 为 `127.0.0.1`；public exposure 需要 explicit opt-in + auth + network controls。

## 12. Desktop App Surface（未来打包目标）

> 本节描述的是 v1.0 方向的**原生桌面应用打包**，不是 v0.1 现实。v0.1 以 CLI + 本地 Web 网关交付，桌面应用在此作为统一分发与最高保真 inspection 的增强目标。

### 12.1 主职责（目标）🔲
- 托管本地 gateway 和 runtime；
- 管理 workspace files、`LOOP-STATE.json`、worktrees、artifacts、memory；
- 启动并监督 coding agents；
- 提供 richest inspection surface：loop/goal state、run log、approvals、cost、skills、diagnostics；
- 管理本地 channel adapter status 与 operator controls（v0.2）。

### 12.2 主要界面区域（目标）🔲
- Workspace：当前 Loop、active Goal、pending decisions、next suggested action。
- 项目 / Loop 切换器：在侧栏切换空间与连续工作流。🔲
- Agents：providers、adapters、runtime status、account/usage view、rate-limit awareness。
- Run log：started、acted、escalated、approved、rejected、cost、outcome history。
- Approvals：sensitive action queue，支持 approve/reject/snooze。
- Memory and skills：browse、inspect、replay、mount reusable workflow knowledge。
- Artifacts：generated reports、code、exports、replay packs。
- Worktrees：active isolation contexts、branch/commit context、cleanup candidates、audit snapshots。
- Channels：adapter status、transport state（v0.2）。
- Settings：gateway、provider、adapter、budget、safety、network、update preferences。

### 12.3 Runtime 行为（目标）🔲
- 默认在本地 loopback 上启动 gateway；
- 从 transient runtime/adapter failures 中 auto-recover，且不丢失 workspace state；
- 在启动本地 coding CLIs 时保留 terminal/session fidelity；
- 即使 web 或 IM 也处于 active，也要通知 desktop user approvals、budget alerts、completion events。

## 13. Web Surface Specification ✅

### 13.1 分发角色
- Web 是 public entry point：download、release notes、platform requirements、setup guidance、operator docs。
- Web MUST 明确传达 local-first 定位：full fidelity 需要本地 runtime（CLI 或未来桌面包）。

### 13.2 Guided Setup 角色
- Web setup 引导 provider auth、workspace template、MCP/ACP adapter onboarding、safety defaults。🔲 channel enablement 留 v0.2
- Web setup 生成或验证本地 workspace initialization，但不替代 runtime authority。
- 每个配置动作都必须映射到 safe local workspace behavior。

### 13.3 Inspection 和 Control 角色
- Web inspection 展示 workspace state、active runs、approvals queue、recent artifacts、memory highlights、skills、channel status。⏳ channel status
- Web control 默认 read-only inspection；explicit operator enablement 后才允许 approval actions 和 bounded continuation commands。
- Web MUST NOT 暴露 unbounded shell、raw local filesystem editing、team-room semantics。

### 13.4 Web Recovery Path
- runtime unavailable 时，web 可显示来自本地 workspace export/sync cache 的最近已知 state。
- IM 无法承载 artifact 或长解释时，web 作为 richer recovery surface。
- Web SHOULD graceful degrade：显示 status、pending actions、reconnect guidance，而不是 silently fail。

## 14. IM Remote-Control Specification ⏳

### 14.1 v0.2 已支持范围（已决策，实现待排期）
- Approved platforms：Slack Socket Mode、Feishu/Lark WebSocket/long-connection、DingTalk Stream、WeCom webhook + explicit public-URL review gate。
- Read commands：`/help`、`/status`、`/current`、`/list`、`/history`、`/memory`、`/skills`、`/model`、`/abort`。
- Write commands：`/new`、`/approve`、`/reject`、`/cancel`。
- Compact notifications：completion、escalation、cost alert、approval request、attention hint。
- IM 能力源自 LoopDesk `channels/` 模块，作为 v0.2 渠道适配器基础。

### 14.2 IM UX 边界
- 第一个 IM 动作是 choosing or inspecting a workspace，而不是 unbounded loop execution。
- IM replies 保持 compact 和 plain-text friendly；长内容要 summarized 并指向 desktop 或 web。
- IM 不替代 desktop/web artifact review；large artifacts、diffs、replay packs 保留在 desktop/web。
- IM commands 是现有 safe workspace actions 的 alias。

### 14.3 IM Safety Model
- IM adapters 默认 disabled-by-default。
- Unknown senders 视为 viewers 或直接拒绝 write commands。
- Write commands 需要 allowlist、budget/kill-switch checks、approval flow、audit logging。
- Channel failure MUST NOT corrupt `LOOP-STATE.json`、memory、skills、artifacts、worktrees。
- Disabling any adapter MUST 保留所有本地 workspace data 和 local runtime behavior。

## 15. 用户界面原则

### 15.1 跨端统一状态
- CLI / Web / IM MUST 显示同一 authoritative workspace state。
- State conflict 由本地 workspace 决定，而不是 chat history 或 IM last-write-wins。
- 每个 surface 都清楚说明 durable source of truth 是本地 workspace。

### 15.2 Local-first Fidelity
- 本地 runtime（CLI + Web）是最高 fidelity surface：editing、review、runtime control、long debugging。
- Web 和 IM 是 continuation/control surfaces，不是 reduced-fidelity replacements。

### 15.3 Continuity Over Rebirth
- 从 CLI 到 web 到 IM 应该像同一任务的不同视角切换。
- 开发者不应需要重新粘贴 project rules、recent decisions、current Goal criteria。

### 15.4 Action Economy
- 每个 remote surface action 应只产生一个清晰结果：inspect、continue、approve、reject、notify。
- docs 和 Web/CLI surface 默认呈现 Markdown-first、可被 LLM 直接引用的信息结构；开发者或代理可用 plain text / JSON 继续工作，而不必重新组织上下文。🔲 v1.0 docs ergonomics
- 避免在 CLI / web / IM 之间复制同一 workflow；保持一个 canonical command model，多个 surface renderings。

## 16. 分发与部署

### 16.1 当前分发路径（CLI + Web）✅
- 主安装路径：CLI（`loopdesk`）+ web-guided setup 用于 local gateway 和 workspace initialization。
- 产品 MUST 明确说明 full fidelity 需要本地 runtime。

### 16.2 未来桌面分发（v1.0 目标）🔲
- 原生桌面包（macOS / Windows / Linux）作为分发增强目标，提升安装与最高保真 inspection 体验。
- 桌面包不引入额外产品叙事；其运行时与 CLI + Web 共享同一本地 workspace 权威。

### 16.3 Web 分发 ✅
- Public web presence 支持 download、docs、setup wizard、release notes、changelog、operator guidance。
- Web 可托管 lightweight operator/account utilities，但 cloud-hosted execution 不是 default narrative。
- Web pages MUST NOT 暗示 mandatory cloud accounts、team rooms、SaaS runtime。

### 16.4 Local Gateway Exposure ✅
- 默认 gateway binding 为 `127.0.0.1`。
- Public exposure 需要 explicit opt-in、authentication、network controls、documented risk acceptance。
- IM webhook channels 需要 explicit review gate 和 documented tunnel、secret rotation、exposure risk。

## 17. Success Metrics

- Context re-entry time：跨工具或跨 surface 重新解释上下文的时间是否下降。
- Loop completion rate：loop/Goal 达到 defined stop condition 的比例。
- Cross-tool fidelity：handoff 保留 task state、decisions、artifacts 的比例。
- Surface adoption：approved work 从 CLI / web / IM 继续且无 data loss 的比例。
- Cost predictability：loop runs 落在 budget 和 escalation threshold 内的比例。
- Remote approval latency：从 IM approval request 到本地 run log 记录决策的时间。
- Recovery success：interrupted runs 从 CLI / web / IM 恢复且无 state corruption 的比例。
- Onboarding completion：首次 setup 内完成"项目选择 / Loop 选择 / resume 或新建 Goal"的比例；v1.0 以 handoff clarity 作为 primary success metric。🔲 v1.0 handoff metric

## 18. Launch Criteria

### 18.1 CLI + 本地 Web Launch（v0.1）✅
- runtime 可安装并初始化 workspace、gateway、local web control surface。
- `LOOP-STATE.json`、memory、skills、artifacts、worktree isolation 可用且可检查。
- 至少一个本地 coding workflow 通过 MCP 或 ACP 接入，并记录在 workspace state。
- Loop engine 支持 triage、maker/checker、run log、approvals、budget controls、stop conditions。
- Local web UI 支持 guided setup、inspection、approvals、diagnostics、export。
- Docs 覆盖 install、connect tools、inspect state、run loops、recover from failures、boundary limitations。
- Setup docs 明确说明如何完成首次 handoff：创建 project、选择 Loop、选择 worktree、resume Goal；避免用户在文档中自行拼凑下一步。🔲 v1.0 guided handoff docs

### 18.2 项目 / 多 Loop 模型 Launch 🔲
- 项目切换器与 Loop 切换器在 CLI / Web UI 可用，切换即切换 Workspace 上下文。
- 新建任务必选归属项目 / Loop（缺省默认当前），保障每个空间状态一致。

### 18.3 Web Launch ✅
- Public web presence 支持 download、setup guidance、operator docs。
- Local web UI 不需要 cloud account，且保持 workspace-first。
- Web setup 和 inspection MUST NOT 默认暴露 team-room、cloud-sync、IM-first narratives。

### 18.4 IM Launch（v0.2）⏳
- IM adapters 默认 disabled，可在不删除本地 workspace data 的前提下启用。
- Approved read commands 支持 workspace selection、status、memory、skills、history。
- Approved write commands 支持 `/new`、`/approve`、`/reject`、`/cancel`，并带 audit logging。
- Budget-cap exceeded、escalation、approval events 生成 compact notifications；v0.2 不发送 large artifacts 或 raw dumps。
- Disabling any adapter 保留本地 loop workspace behavior。

### 18.5 Quality and Safety ✅
- Focused functional gate 通过：loop workspace、CLI、gateway、web UI static views。⏳ channel adapter core behavior（v0.2）
- 没有 public docs、web UI、IM narrative 泄露 team collaboration、cloud-first sync、channel-first messaging 作为主产品。
- Operator 可 disable channel adapters 并保留完整本地 loop workspace 功能。
- 公共文档、Web UI、IM narrative 优先呈现 personal loop continuity；若需引用 Raft-style shared-room 或 cloud-sync 叙事，必须显式标注为 LoopDesk 不做方向。🔲 v1.0 anti-room guardrail

## 19. Roadmap Alignment（统一视图）

### v0.1 Baseline（已实现）✅
- 本地优先的 personal loop workspace：`LOOP-STATE.json`、MCP-first、ACP-second、loop engine、memory、skills、artifacts、cost/safety controls、worktree isolation、CLI、local web UI。

### v0.2 Baseline（已决策，实现待排期）⏳
- Optional IM channel adapters 保持 secondary to local workspace（能力源自 LoopDesk `channels/`）。
- Web inspection surface 扩展到 channel status、approval actions、operator setup。
- IM 仅作为 continuation/notification surface；不跑 chat-first loop execution。

### v1.0 Direction（设计中）🔲
- 原生桌面应用打包、auto-update、richer desktop inspection。
- 项目 / 多 Loop 空间模型在 CLI / Web UI 全面落地。
- Web-assisted guided setup、operator onboarding、multi-surface approval。
- IM remote continuation 扩展到更多 approved bounded Goal patterns。
- 内部 Python 包名从 `loopdesk` 全量迁移到 `loopdesk`。
- Setup + docs + web/IM handoff 以 Raft 的“清晰下一步任务”为借鉴，但保持 personal-first、local-first、loop-state-first；不引入 room-first 或 cloud-first narrative。🔲 v1.0 guided onboarding/offboarding

## 20. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| 用户仍把 Web/IM 当主产品 | 持续锁定 local-first 叙事、local gateway authority、state ownership |
| 桌面打包周期长 | Web + CLI 承担 onboarding/setup，明确标注 full fidelity 需要本地 runtime；桌面包为 v1.0 增强 |
| IM 继续膨胀成执行面 | disabled-by-default、allowlist、budget/kill-switch、command allowlist、audit log |
| 多端状态不一致 | 唯一 durable source of truth 仍是本地 `LOOP-STATE.json`；三端只读或回写 |
| 远端继续引发高风险执行 | 仅 approved bounded work 可继续；高风险工作继续 approval-gated + local-oriented |
| 项目/Loop 上下文串扰 | 新建任务必选归属项目/Loop；每 Goal worktree 隔离 |
| 文档口径分裂 | 本 PRD 作为后续 docs、release notes、setup、landing page 的共同边界 |

## 21. Open Questions（已解决项见 §3、§7、§8.5）

- 桌面应用采用 Electron shell，还是"本地 runtime + 系统 launcher"？🔲 留 v1.0 决策。
- 项目 / 多 Loop 模型的 CLI 与 Web UI 交互细节是否需要独立 feature plan？🔲 是，需补 `docs/plans/`。
- IM 后续是否扩大平台集合；扩大前需要哪些 operator controls？⏳
- 内部包名 `loopdesk` → `loopdesk` 的全量迁移成本与窗口？🔲 留 v1.0+。
- 是否应在 v1.0 引入更明确的 Skills/MCP marketplace 或 share 机制；若引入，如何避免偏离 personal-first？

## 22. Approval

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
| QA | | Pending |
