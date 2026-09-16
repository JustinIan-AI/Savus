# 术语表

本术语表用**面向用户的白话**定义 LoopDesk 与循环工程的常见术语。它不是运行时设计文档。

## 命名与使用约定（2026-09-16 起）

1. **中文为主**：正文首次出现写「中文名（English）」，其后**只用中文名**。本表的小节标题同样以中文名开头。
2. **命令、字段名、枚举值保持原样**：它们必须可复跑，不做翻译。例：`waiting_on=controller`、`--capability-gap-status`。
3. **检索方式**：本表按**中文名拼音**（第一部分）与**所属层**（第二部分）排列，不按英文字母序。想查英文词，直接 `Cmd/Ctrl+F` 搜英文名。
4. **这张表管"叫什么"，不管"怎么走"**：完整流程见
   [`plans/2026-09-16-issue-fix-end-to-end-flow.zh.md`](plans/2026-09-16-issue-fix-end-to-end-flow.zh.md)。

---

# 第一部分 · LoopDesk 产品概念

> 这部分是 LoopDesk 自身的能力词汇，按中文名拼音排序。

## 本地网关（Gateway）

Web UI、渠道、会话、审批、诊断、用量与 RPC 客户端背后的本地服务器。

阅读：[`gateway.md`](gateway.md)

## 重放（Replay）

从决策日志对某个已记录回合的只读查看。重放不会重新运行工具。

阅读：[`diagnostics-and-replay.md`](diagnostics-and-replay.md)

## 调度器（Scheduler）

`loopdesk cron` 功能，用于周期性与一次性的 LoopDesk 运行。

阅读：[`scheduling.md`](scheduling.md)

## 工具压缩（Tool Compression）

一种节省上下文的功能：在保留大型工具结果可用性的同时，只向模型发送更小的预览。

阅读：[`features/tool-compression.md`](features/tool-compression.md)

## 工作区（Workspace）

任务被允许或预期在其中工作的本地目录。工作区 flag 有助于限制文件与 shell 操作范围。

阅读：[`tools-and-sandbox.md`](tools-and-sandbox.md)

## 会话（Session）

一段可持久化的对话或任务历史。会话可被列出、恢复、导出、终止或删除。

阅读：[`sessions.md`](sessions.md)

## 交付物（Artifact）

一次运行产生的文件或媒体输出，例如 HTML 页面、报告、图片、表格、PDF 或幻灯片。

阅读：[`artifacts-and-media.md`](artifacts-and-media.md)

## 技能（Skill）

可复用的任务专用指导、脚本或工作流指令包，LoopDesk 可在需要时加载。

阅读：[`features/skills.md`](features/skills.md)

## 记忆（Memory）

可持久化的用户或项目上下文，之后可被搜索与召回，而无需把每段旧对话都塞进当前 prompt。

阅读：[`features/memory.md`](features/memory.md)

## 路由层（SquillaRouter）

LoopDesk 的本地路由层，用于为每个回合选择合适的模型档位。

阅读：[`features/squilla-router.md`](features/squilla-router.md)

## 模型服务商（Provider）

为 LoopDesk 配置的模型后端，例如 OpenRouter、OpenAI、Anthropic、Gemini、DeepSeek、DashScope 或 Ollama。

阅读：[`providers-and-models.md`](providers-and-models.md)

## 渠道（Channel）

一种消息集成，例如 Telegram、Slack、飞书/Lark、Discord、钉钉、WeCom、Matrix、终端或 websocket 风格客户端。

阅读：[`channels.md`](channels.md)

## 权限配置（Permission Profile）

一次运行所选的工具访问姿态，例如 `restricted`、`on`、`bypass` 或 `full`。

阅读：[`approvals-and-permissions.md`](approvals-and-permissions.md)

## 审批（Approval）

敏感工具动作继续之前所需的人工决策。审批行为取决于使用面、权限配置与工具策略。

阅读：[`approvals-and-permissions.md`](approvals-and-permissions.md)

## 压缩（Compaction）

在长会话中缩减旧上下文的过程，使智能体能在模型的上下文预算内继续。

阅读：[`features/compaction-and-cache.md`](features/compaction-and-cache.md)

## 元技能（MetaSkill）

可复用、可审计的工作流协议，把多个技能、工具、模型调用、检查或输出步骤组合成一个可重复的能力。

阅读：[`features/meta-skills.md`](features/meta-skills.md) 与 [`features/meta-skill-user-guide.md`](features/meta-skill-user-guide.md)

## 诊断（Diagnostics）

用于理解路由、服务商行为、压缩、工具压缩、缓存行为与投递失败的运行时日志开关。

阅读：[`diagnostics-and-replay.md`](diagnostics-and-replay.md)

## 智能体（Agent）

一个具名的 LoopDesk 身份，带有模型、工作区、名称与描述等默认值。内置的 `main` 智能体始终可用。

阅读：[`agents.md`](agents.md)

---

# 第二部分 · 循环治理术语

> 一个长任务被「管起来」时用的通用词汇。这部分**跨 LoopDesk / LoopX / Agent Runtime 三个系统**，所以每条都标注了它属于哪一侧，避免张冠李戴。

## 2.1 任务控制面（LoopX 侧）

### 目标（Goal）

一件长期要做成的事。任务控制面的顶层单位，所有待办都挂在某个目标下。

> 在本项目里：`savus-goal` 就是本仓库的目标，记在 `.loopx/registry.json`。

### 待办（Todo）

目标下面的一步。可以指派给人，也可以指派给智能体（看 `role` 字段）。

### 切片（Slice）

一次能做完、并且能被验证的一小块工作。整个控制面的设计目标就是「让每次只推进一个有界的切片」。

### 轮次（Turn）

智能体的一次执行回合。「算力配额」按轮次计数，所以**轮次是成本的计量单位**。

### 状态回写（State writeback）

干完活之后，把结果写回状态文件。**不写回就不算完成** —— 这是控制面的硬规定。

### 活跃状态（Active state）

单个目标当前处在什么状态的记录，落在 `.codex/goals/<目标id>/ACTIVE_GOAL_STATE.md`。

### 注册表（Registry）

目标与适配器的清单。分项目级（`.loopx/registry.json`）与全局级（跨项目仪表盘的真源）。

### 待处置队列（Attention queue）

「现在需要谁动手」的队列。这一份队列就能撑起整个界面的待办提示。

### 等待方（`waiting_on`）

当前这个目标在等谁。取值如 `controller`（等值守人）、`agent`（等智能体）、`user`（等用户）。

> **最容易用错的地方**：看板「评审中」这一列不是手工拖进去的，它应当由 `waiting_on=controller` 直接决定。

### 严重度（`severity`）

这条待处置事项有多急，取值如 `action` / `info`。用来决定卡片要不要高亮。

### 任务类别（`task_class`）

待办的种类：`advancement_task`（推进型）/ `continuous_monitor`（持续监视型）/ `user_gate`（等人工门）/ `user_action`（等人工动作）/ `blocker`（阻塞项）。卡片上的类型徽标读它。

### 依赖血缘（`successor_todo_id` / `unblocks_todo_id`）

待办之间的先后关系：A 做完会自动激活 B。界面上的「进度明细」应该把它画出来，而不是画一串固定阶段。

### 监视目标键（`monitor_target_key`）与状态桶（state bucket）

持续监视型待办不按「每个对象一个待办」建，而是按**状态桶**合并成一个待办，避免待办数量爆炸。

### 运行日志（Run log）

控制面记录的历史。用于回溯「这一步到底发生了什么」。

### 证据账本（Evidence log）

每个智能体名下的精简账本，记录它做过什么、有什么证据。是交接与重规划前必读的东西。

### 产出度量（`outcome` / `metrics`）

一次修复结束后，对「产出了什么、仓库变了多少、还缺哪些数据」的盘点。注意 `outcome` 只是**投射**（读已有事实，不产生新事实）。

### 投射（Projection）

把已有状态**重新表达**成另一种视图，本身不改变事实。看到「投射」二字，就理解为「只读的重新呈现」。

---

## 2.2 能力供给面（Agent Runtime 侧）

### 运行时（Agent Runtime）

真正执行智能体回合的系统：宿主应用、技能装载、工具与沙箱、外部服务连接。**决定「能做什么、怎么跑」的是它**。

> LoopX 认可 19 种运行时类型，用 `loopx agent-onboard --list-agent-types` 可列出。

### 运行时类型（`agent_type`）

运行时的受约束枚举值，例如 `codex-app` / `claude-code` / `cursor-agent` / `manual`。

> **注意**：`codex` 是**歧义值**，会被拒绝，必须四选一。所以界面里运行时名称应该是**下拉枚举**，不能是自由文本。

### 技能作用域（skill scope）

技能装在哪一层：项目级 / 用户级 / **按运行时分散**（如 `GEMINI_HOME/skills`、`CURSOR_HOME/skills`）。

### 受管技能（managed skill）

由系统投递、并受系统卸载管理的技能副本。卸载时**只删未被用户改动过**的那些 —— 所以界面要区分「已启用」与「已修改」。

### MCP 服务（MCP server）

**Agent Runtime 侧**的工具服务接入（`MCP` = Model Context Protocol，模型上下文协议）。它决定智能体能调用哪些外部工具。

> 归属：**Agent Runtime 侧**。「接哪些工具服务、怎么接」由运行时决定；任务控制面只负责声明「需要什么能力」。

### 数据连接器（Connector / `loopx connector list`）

LoopX 自己维护的**数据源注册表**（带 `layer` / `value` / `score` 排序），用于挑选外部数据来源。

> **与 MCP 服务不是一回事**：连接器是「去哪里取数」，MCP 服务是「智能体能调用什么工具」。两者没有从属关系，**不要画在同一分组下**。

### 能力（Capability）

「这套运行时能做某件事」的声明。是两层之间最关键的接口词汇。

### 可用能力（`available_capability`）

运行时**声明**自己具备的能力（在接入时提供，可重复多项）。是**供给侧**。

### 能力缺口（Capability gap）

**需求侧**（这个待办需要什么能力）减掉**供给侧**（运行时具备什么能力）之后的空隙。缺口状态分三级：`found`（发现）/ `fixed`（已补）/ `real_callsite_verified`（真实调用点已验证）。

> 这是最值得做成界面对象的一项：列表上最该高亮的，不是「有哪些技能」，而是「这个任务缺什么」。

---

## 2.3 交接与验收

### 契约包（Packet）

系统给出的、机器可读的指令与约束集合。**它只是契约，不是执行** —— 拿到包之后，分析或干活的是智能体。

> 关键证据：`loopx todo suggest` 返回 `loopx_role: prompt_contract_only`、
> `analysis_owner: user_project_agent`，原文写明「LoopX 只给分析契约，它自己并不分析仓库」。

### 交接（Handoff）

把任务交给下一轮或下一个执行者。交接前系统会先判断「现在能不能交」。

### 交接接口预算（Handoff interface budget）

交接包的大小上限（实测 `max_lines=16`、`max_chars=1800`）。它的存在说明**交接必须精简**，不能把整段历史塞过去。

### 就绪阻断项（Readiness blocker）

「还差哪几项才能交付」的显式清单，例如 `approved_repo_context_missing`、`validation_not_run`。

> 界面应展示**清单**，而不是一个灰色的「未就绪」按钮 —— 灰按钮不告诉用户差什么。

### 固化样本（Fixture）

可**离线复跑**的验收样例。它让「修好了吗」这个问题有一个不依赖网络的确定性答案。

### 复现（Reproduction / repro）

先把问题**重新跑出来（并且失败）**，再谈修复。

### 验证（Validation）

用仓库自己的命令证明修复有效。和「复现」是**两件事**。

> **两段式验证**：先复现失败 ✗，再验证通过 ✓。界面必须画成两个徽标，不能合并成一个对勾 —— 只有一个对勾就分不出「真的复现过」还是「跳过了」。

### 分诊（Triage / `feasibility`）

判断一个问题值不值得修、该怎么修，并且**恰好选一条路**。

### 路由（Route）

分诊的三种产出：`fix_pr`（备修复 → 界面显示「备修复」）、`comment_only`（仅评论）、`triage_only`（仅记录）。

> `triage_only` 的存在是一种**产品表态**：允许不做，而不是硬凑一个补丁。

### 受理 / 准入（Admission）

「这个候选够格进入下一道工序吗」的检查点。常见取值 `evidence_required` —— 证据不足直接拦下。

---

## 2.4 治理与安全

### 审批门（Gate）

必须人点头才能继续的关卡。**任务级**概念（对比「权限配置」是运行级姿态）。

> 它不是写死的文案：目标会声明「哪几类动作需要放行」（如 `write` / `publish` / `production-action`），
> 界面应当读这个声明来渲染。

### 值守人（Operator）

负责做人工决策的角色。它的决策带一个**必填理由** —— 强制留痕。

### 算力配额（Quota）

「还能跑几轮」。它决定下一步是「可执行」还是「暂停」。

> 配额不足时系统会给出**卡住的原因**（如「配额处于人工门状态」+「还有可见的开放待办」），
> 界面应该把原因显示出来，而不是只显示一个灰色的禁用态。

### 认领（Claim）

把某个待办归到某个执行者名下（软性）。

### 租约（Lease）

比认领更强的所有权：有期限、可续期、可转移、可释放。租约的有效期与状态都是界面要显示的信息。

### 静止态（Quiescent）

「没有正在被认领的待办、也没有生效中的租约」的状态。某些切换操作（如改所有权模式）要求先进入静止态 —— 这是一条**并发安全的产品约束**。

### 自愈（Self-repair）

流程的异常分支，五步：先**停止投递（不再消耗配额）** → 建紧凑证据包 → 归类失败 → 归属到具体的责任层 → 在**最低的持久层**修根因。

> 它是一个独立告警条该承载的内容，而不是混在正常进度里。

### 公开安全（Public-safe）

可以外传、不含私有信息的状态表达。系统会显式标注「是否读了私有仓库状态」「是否记录了本地路径」。

### 有界（Bounded）

有明确上限（条数、字符数、轮次）。循环工程里几乎所有动作都被要求有界。

### 节奏（Cadence）

工作推进的粒度，实测取值 `bounded_progress_segment`（一段一段有界推进）。它不是时间频率，而是**推进方式**。

### 记账规则（Spend rule）

什么时候扣配额的规则。实测取值 `spend_only_after_artifact_validation_writeback` —— **先产出产物、验证、写回状态，才允许记账**。

### 不变式（Invariant）

不允许被破坏的硬规定（例如「复现必须先失败」）。界面上的红线大多来自不变式。

---

# 第三部分 · 遗留词 → 现行词

> 早期文档里的用词，遇到时按下表换读。

| 遗留词 | 现行词 | 说明 |
|---|---|---|
| session（作为顶层单位） | 循环 / 目标 | 会话已降为「手动动作渠道」，不再是主对象 |
| chat | 任务 / 待办 | 对话是任务的载体，不是任务本身 |
| cron | 调度器 | 内部能力，不作为对外主词汇 |
| workspace-state.json | `LOOP-STATE.json` | 可移植的循环状态文件 |
| personal loop workspace | **团队循环工作区** | v0.1 单人定位已作废 |
| issue-fix 的「阶段①②」＝ MCP / Skills | 归属**运行时**，不是控制流程的阶段 | 见第二部分 2.2 |

---

[文档索引](README.md) · [循环流程文档](plans/2026-09-16-issue-fix-end-to-end-flow.zh.md) · [改进此页](contributing-docs.md)
