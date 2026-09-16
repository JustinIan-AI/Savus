# 自动修复场景 · 端到端操作流程（原型设计输入）

> Status: v0.2 设计输入（draft）
> Date: 2026-09-16
> Author: design partner（WorkBuddy 智能设计助手）
> 对标对象: 本机部署的 **LoopX v1.0.2**（`loopx` CLI：`/opt/homebrew/bin/loopx` → `~/.local/share/loopx-venv/bin/loopx`）
> 事实来源: 全部命令输出、契约包字段、状态文件路径均**实机跑出**，非文档转述
> 配套: `docs/research/competitive-intel-huangruiteng-loopx.md`（认知层）、`docs/decisions/loop-management-optimization.md`（建议层）、`docs/glossary.md`（**术语层**）、本文（**流程层**）
> 用途: 作为**细化 `frontend/` 原型**与主画布 `724693301521075` 的流程依据 —— 每个流程节点都能落到具体的 UI 承载位

---

## 0. 本文的范围与阅读方式

**本文回答一个问题：一次「自动修复」从任务产生到收尾，在控制面上发生了哪些步骤，每一步由哪个字段决定。**

- 对**任务控制面（LoopX）**：给权威结论（实机取包，v1.0.2）；
- 对**能力供给面（Agent Runtime）**：**只定义交界** —— 控制面需要什么、运行时声明什么、缺口怎么呈现。运行时内部的技能发现机制、MCP 服务配置与凭证管理不在本文范围，那是运行时自身的设计范畴。

**建议阅读顺序**：

1. **§1 两层架构** —— 决定原型的信息架构（哪几个页面属哪一层）；
2. **§5 字段驱动总表** —— 决定每个 UI 元素读什么字段；
3. **§8 设计点** —— 决定要改哪些画布节点。

**命名约定**：专有名词中文为主，首次出现写「中文名（English）」，其后只用中文名；命令、字段名、枚举值保持原样以可复跑。全部术语的权威释义见 `docs/glossary.md`。

---

## 1. 两层架构：任务控制面 × 能力供给面

原型最容易画错的地方，是把两个系统画成一条流水线。真实结构是**两层 + 一个交界**：

```
┌──────────────────── L2 能力供给面（Agent Runtime）────────────────────┐
│  运行时类型 · 技能装载 · MCP 服务 · 轮次执行 · 工具与沙箱            │
│  原型页面：设置·MCP（04）· 团队资产（02）· 设置·Agent（03）           │
│                                                                      │
│   声明：我能做什么（available_capability / 已装载技能 / 已注册服务）  │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  交界契约（唯一耦合点）
                    ┌───────────┴───────────┐
                    │  需求 ←→ 声明 ←→ 缺口 │
                    │  required_capability  │
                    │  available_capability │
                    │  capability_gap_...   │
                    │  handoff 接口预算     │
                    └───────────┬───────────┘
┌───────────────────────────────┴──────────────────────────────────────┐
│                      L1 任务控制面（LoopX）                           │
│  目标 · 待办 · 状态 · 证据 · 配额 · 租约 · 审批门                      │
│  原型页面：任务看板（01）· 右栏 · 新建任务（09）                       │
│                                                                      │
│   产出：有界「契约包」（packet）—— 只给分析契约，不代替执行            │
└──────────────────────────────────────────────────────────────────────┘
```

**两层的分工边界**（这是原型信息架构的根据）：

| 层 | 管什么 | 谁拥有 | 生命周期 | 原型承载 |
|---|---|---|---|---|
| **L2 能力供给** | 运行时能否跑、装了哪些技能、接了哪些服务 | **Agent Runtime** | 天级 / 周级 | 设置·MCP（04）· 团队资产（02）· 设置·Agent（03） |
| **L1 任务控制** | 目标是什么、任务从哪来、做到哪一步、能不能推进 | **LoopX** | 分钟级 / 秒级 | 任务看板（01）· 右栏 R1–R8 · 新建任务（09） |

**一句话记住**：LoopX 决定「该做什么、做到哪了」，Runtime 决定「能做什么、怎么跑」。原型的两组页面各自对应一层，不要混着设计。

---

## 2. L2 能力供给面（Runtime）—— 只定边界

> 本节不描述 runtime 内部的技能加载与 MCP 配置机制。这里固定的是**两层之间的交界**：LoopX 需要什么、Runtime 声明什么。

### 2.1 LoopX 认可的 19 种运行时类型

`loopx agent-onboard --list-agent-types` 的权威清单。**这张表本身就是原型「运行时接入」分组的候选枚举**：

| `agent_type` | 宿主循环（Host loop） | 入口 |
|---|---|---|
| `ark-managed-agent` | 由 Goal 运行时持有的一次性目标激活 | 提交生成的 `task_body` |
| `codex-app` | Codex App 心跳自动化 | `$loopx <task>` 或 `/skills` 里的 LoopX 技能 |
| `codex-app-ssh` | SSH 下无自动化时的可见 `/goal` | 同上 |
| `codex-cli` | 可见 Codex CLI `/goal` | 同上 |
| `codex-ide-plugin` | 可见 Codex IDE 插件 `/goal` | 同上 |
| `claude-code` | 原生 `/loop`，由 LoopX 把关 | 先 `/loopx <task>`，再 `/loop` |
| `kunluncode` | 由 LoopX 控制的可恢复原生 Goal Pro | `loopx-kunluncode add` → `run` |
| `opencode` | 可见 OpenCode goal 插件，由 LoopX 把关 | `/loopx <task>` + OpenCode 桥接 |
| `opencode2` | 由 LoopX goal worker 驱动的可见 OpenCode 2 会话 | `/loopx <task>` + OpenCode 2 |
| `traex-cli` | 可见 TraeX `/goal`，由 LoopX 把关 | `$loopx <task>` 或技能 |
| `pi` | 可见 Pi goal 扩展，由 LoopX 把关 | `/loopx <task>` + Pi 扩展 |
| `gemini-cli` | agent 驱动的 Gemini CLI 循环，受配额把关 | `GEMINI_HOME/skills` 中的 LoopX 技能 |
| `cursor-agent` | agent 驱动的 cursor-agent 循环，受配额把关 | `CURSOR_HOME/skills` 中的技能 **+ 已注册的 LoopX MCP 服务** |
| `zcode` | agent 驱动的 ZCode 循环，受配额把关 | `ZCODE_HOME/skills` 中的技能 |
| `agy` | Antigravity CLI 原生 `/goal` 循环（自带定时唤醒） | `~/.gemini/antigravity-cli/skills` 中的技能 |
| `deepseek-harness` | DeepSeek Harness 无头/自动化循环 | `loopx turn run-once`（`loopx.dsh_goal_mode`） |
| `deepseek-harness-native` | 由 LoopX 插件驱动的同会话循环 | 技能 + DSH `/loopx-init` |
| `manual` | 外部调度器或人工的配额/状态循环 | CLI 契约包 + 外部驱动 |
| `other-agent` | 自定义 agent 循环驱动 | `@loopx <task>` / `$loopx <task>` |

**两个观察，直接可用于原型**：

1. **技能目录与 MCP 注册按 runtime 分散**（`GEMINI_HOME` / `CURSOR_HOME` / `ZCODE_HOME` / `~/.gemini/antigravity-cli` …）—— 所以「团队资产」页的**作用域**不只有「项目 / 用户」，还有**「按 runtime 分散」**这一维；
2. **只有部分 runtime 需要 MCP 注册**（表里只有 `cursor-agent` 明确要求），且 `codex` 是**歧义值**，会被拒绝并提示改为四选一。→ 原型里 runtime 名称应该是**受约束的枚举选择器**，不是自由文本。

### 2.2 LoopX 对 Runtime 只做三件事

| 事 | 命令 | 边界 |
|---|---|---|
| **投递宿主适配文件** | `loopx slash-commands --install` | 只写自己的 `loopx-*` 文件到宿主技能目录，不改宿主技能体系 |
| **装载/卸载受管技能** | `loopx workflow-skills` · `loopx project-skill {status,install,uninstall}` | `uninstall` 只删**未被改动**的受管副本（用户改过的不删） |
| **生成接入包** | `loopx agent-onboard --agent-type <t> --project .` | 产出的是**给 runtime 执行的指令**，LoopX 不代替 runtime 执行 |

`loopx doctor` 会校验这三件事的结果：

```
- installed_skill: ~/.codex/skills/loopx-project/SKILL.md
- skill_delivery_mode: surface_managed
- skill_delivery_status: repair_recommended        ← 三态之一
- installed_required_skills: loopx-benchmark, loopx-doc-registry,
  loopx-pr-program, loopx-pr-review, loopx-project, loopx-self-repair
- runtime_projection_routes_healthy: True
- typescript_control_plane: ready / typescript_runtime_state: stopped
```

→ 这是「连接器卡片状态徽标」的信息密度来源：**已就绪 / 待修复 / 未安装** 三态 + 逐项 `valid:True/False` + 路径 + 修复建议。

### 2.3 能力缺口：两层之间唯一真正需要设计的对象

LoopX 侧声明**需求**，Runtime 侧声明**供给**，中间的空隙就是**能力缺口**：

| 侧 | 字段 / 参数 | 含义 |
|---|---|---|
| 需求侧 | `--required-capability` | 这个待办**必须**具备的能力 |
| 需求侧 | `--target-capability` | 希望引入的能力（可为缺口） |
| 需求侧 | `--required-write-scope` | 允许写的范围（与审批门联动） |
| 缺口态 | `--capability-gap-status {found,fixed,real_callsite_verified}` | 缺口从「发现」到「真实调用点已验证」的三级 |
| 供给侧 | `agent-onboard --available-capability <c>`（可重复） | 当前宿主循环具备的能力 |
| 供给侧 | `loopx connector list` | 数据连接器注册表（**注意：与 runtime 的 MCP 服务不是一回事**，见 §附录 C） |

**这是本版最重要的新增设计结论**：原型的「团队资产」与「设置·MCP」不应只做**清单**，而应能回答**「这个任务缺什么」** —— 需求侧字段与供给侧声明一相减，缺口就是列表上最该高亮的那一行。

### 2.4 → 原型映射

| 页面 | 当前状态 | 建议 |
|---|---|---|
| **设置·MCP（04）** | 只有一类卡（外部系统） | 按层分两组：**运行时接入**（19 种 runtime，枚举选择）／**外部服务**；卡片带三态徽标 |
| **团队资产（02）** | 卡片类型 `rule/command/skill/mcp` | 补 `runtime` 类型；卡面改为**能力元数据四段**：触发条件 / 依赖能力 / 输出契约 / 作用域；作用域增加「按 runtime」一维 |
| **设置·Agent（03）** | 已有 agent 配置 | 与 runtime 类型枚举对齐（`agent_type` 受约束选择器） |
| **（新增）能力缺口** | 无 | 在看板卡与右栏增加「缺什么能力」提示 —— 由 `required_capability` − 供给侧声明得出 |

**注意**：以上三页的**视觉与信息架构依据来自 Agent Runtime 的能力模型**，本文只提供交界字段。Runtime 侧的完整设计需要单独的事实源。

---

## 3. L1 任务同步（状态面）

### 3.1 两层状态，一个共享真源

```
项目级（每仓库自持）
├─ .loopx/registry.json                         # 目标列表 + 适配器 + 协调策略
└─ .codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md  # 单目标活跃状态

共享级（跨项目仪表盘真源）
└─ ~/.codex/loopx/registry.global.json          # 全局目标路由
   ~/.codex/loopx/                              # 运行历史
```

实测 savus 的 `.loopx/registry.json`（关键片段）：

```json
{
  "goals": [{
    "id": "savus-goal",
    "status": "active",
    "role": "controller",
    "adapter": { "kind": "generic_project_goal_v0", "status": "connected" },
    "coordination": {
      "write_scope": [],
      "requires_parent_approval": ["write", "publish", "production-action"]
    },
    "execution_profile": {
      "cadence": "bounded_progress_segment",
      "minimum_scale": "multi_surface_or_implementation",
      "must_include": ["coherent_artifact", "targeted_validation", "state_writeback"],
      "spend_rule": "spend_only_after_artifact_validation_writeback"
    }
  }]
}
```

两个字段直接决定原型语义（**不要写死文案**）：

- **`coordination.requires_parent_approval`** = 形式化的**审批门**：声明「写 / 发布 / 生产动作」三类需人工放行。右栏「审批门」（画布 `2:213`）应读它渲染，而不是显示固定文案；
- **`execution_profile.must_include`** = **「完成」的定义**：一个切片必须同时产出「连贯产物 + 定向验证 + 状态回写」，且 `spend_rule` 规定**先验证回写、后记账**。这直接回答「什么算完成」。

### 3.2 任务从哪来

```bash
loopx todo suggest --goal-id <id> \
  --from    {recent-repo | issues-prs | failing-checks | todo-markers
             | complexity-hotspots | loopx-deferred | docs-smokes} \
  --trigger {user-requested | post-connect | no-runnable-todo
             | repo-changed | quality-watch} \
  --limit <N>
```

实测返回（这是最容易被误解的一处）：

```
- schema_version: todo_suggestion_prompt_v0
- mode: agent_guided_candidate_todo_queue
- analysis_owner: user_project_agent
- loopx_role: prompt_contract_only
- state_write_performed: False
- formal_todos_written: False
- sources: issues-prs
```

> 原文：**"LoopX is only giving you the analysis contract; LoopX is not analyzing the repository itself."**

**七个来源 + 五个触发时机**，且**分析由 agent 做、LoopX 只出契约** —— 这正是 §1 两层架构的最好证据。→ 看板卡需要「**来源**」这一维（当前完全没有）。

### 3.3 同步到外部看板

```bash
loopx goal-channel {setup|attach|sync|doctor|notify-gate} --goal-id <id>   # 一渠道最多挂 8 个目标
loopx sync-global [--dry-run] [--replace-state]                            # 项目状态 → 全局注册表
loopx refresh-state --goal-id <id>                                         # 刷新陈旧看板投射
```

两条纪律：
- **`sync-global` 不允许手工搬运**（技能原文明确禁止把一个项目的注册项手抄到另一个项目）；
- **外部通知粒度是「一次一个 PR / 一次一个审批门」** —— 防刷屏，是刻意的产品约束。

### 3.4 当前实测状态（字段最全的一次采样）

```bash
$ loopx status
- registry: .loopx/registry.json   goals: 1   runs: 0
- status_contract: schema_version=2   producer=loopx status
- contract: ok=True, errors=0, warnings=0, checks=6
- global_registry: available=True, ok=True, findings=0

## Attention Queue
- summary: items=1, needs_user_or_controller=1, needs_controller=1, needs_codex=0
- `savus-goal`: status=active_state_user_gate  phase=connected
                waiting_on=controller  severity=action  source=active_state
  - execution_profile: cadence=bounded_progress_segment
      include=coherent_artifact,targeted_validation,state_writeback
      spend_rule=spend_only_after_artifact_validation_writeback
  - long_task_cadence_hint: signal=blocked  recommendation=wait
      reasons=quota_state_operator_gate, open_user_todos_visible
  - orchestration: mode=default  spawn_allowed=False  max_children=3
  - asset_todos: user_open=1  agent_open=1
  - asset_quota: compute=1.0  state=operator_gate  slots=0/1440
  - handoff_readiness: ready=False  codex_ready=False  source=project_asset
  - handoff_interface_budget: mode=project_agent_handoff  max_lines=16  max_chars=1800
  - handoff_checks: pass=project_asset_backed,same_source_should_run,
      handoff_has_next_action,handoff_has_stop_condition,handoff_sanitized_surface
      fail=codex_ready
  - handoff_state: status=ready_waiting_for_run  post_handoff_run_seen=False
```

**这一份输出就能撑起整个右栏与看板卡片**。`waiting_on=controller` 是「评审中」列的判据；`handoff_checks` 的 `pass/fail` 是逐项检查清单；`handoff_interface_budget` 是交接包的体积上限。

### 3.5 → 原型映射（任务看板，画布 01）

**四列由字段驱动**（不是手动拖拽）：

| 看板列 | 判据（字段） | 等价命令 |
|---|---|---|
| 待办 | `status=open` 且无 `claimed_by` | `todo list --status open` |
| 进行中 | 有 `claimed_by` 或持有 `task-lease` | `todo claim` 之后 |
| **评审中** | `waiting_on=controller`，或 `task_class ∈ {user_gate, user_action}` | `active_state_user_gate` |
| 已完成 | `status=done` 且已 `state_writeback` | `todo complete` |

另四项建议：**来源芯片**（7 个来源）· **顶栏同步指示**（上次 `sync-global` + 注册表健康）· **左栏待处置计数**（`attention_queue.summary.items`）· **卡片醒目度**（读 `severity`）。

---

## 4. L1 任务处置 —— 自动修复九步

每一步给出**真实命令**与**真实字段**。括号内为中文首选名。

### 第 0 步 · 建目标（goal）

```bash
loopx connect --project .          # 创建/连接项目本地状态
loopx start-goal --guided --project . --goal-text "<目标>"
```

产出 **`goal_start_contract` + `ordered_steps`** —— **先计划、后执行**，这是 LoopX 与「直接开干」的根本分野。

### 第 1 步 · 元数据进场

```bash
loopx issue-fix workflow-plan --url <url> --fetch-metadata --format markdown
```

**公私边界**：`--fetch-metadata` 用 `gh api --jq` **只取紧凑字段**，契约包显式标注 `private_repo_state_read: False`、`local_paths_captured: False`；正文与评论**不复制**。

### 第 2 步 · 仓库上下文（必须 5 方面齐备）

`architecture` / `change_scope` / `ownership` / `reproduction` / `validation`

未提供时的实测输出：

```
## Repository Context
- status: not_provided
- unresolved_required_aspects: ['change_scope', 'reproduction', 'validation']
- expert_next_action: read_repository_sources
```

→ **守卫会拦住，不让你往下走**。这是「证据不足不得开工」的强制实现。
上下文输入契约还带三个受控词表：`source_kind`（9 种）、`trust`（`advisory/authoritative/verified`）、`freshness`（`current/stale/unknown`）—— 可直接做「证据可信度」的 UI 维度。

### 第 3 步 · 候选预检

```
## Candidate Preflight
- admission: evidence_required        candidate_runnable: False
- successor_action_kinds: ['issue_fix_collect_candidate_evidence']

## First Screen
- waiting_on: agent      user_action_required: False      agent_can_continue: True
- next_safe_action: complete the projected source-bound candidate successor,
  then rerun candidate admission; do not enter feasibility or patch planning
```

**`next_safe_action` 是机器可读的「下一步」，且带禁令**（"do not enter feasibility or patch planning"）。→ 右栏「下一步建议」应渲染**带禁令的下一步**，不是散文。

### 第 4 步 · 分诊（恰好三选一）

```bash
loopx issue-fix feasibility \
  --reproduction-status {confirmed|planned|missing|blocked} \
  --scope-class {bounded|uncertain|oversized} \
  --comment-value {none|clarification|diagnosis} \
  --goal-id <id> --format json
```

| 路由 | 优先级 | 含义 | 后续 |
|---|---|---|---|
| `fix_pr` | P0 | 备一个小修复分支、验证、产出评审包 | 进第 5–7 步 |
| `comment_only` | P1 | 起草公开安全的维护者评论，**发帖前需显式审批门** | 止于评论包 |
| `triage_only` | P2 | 记录阻塞或无后续决定，**不开无根据的补丁循环** | 止于记录 |

**分诊的产出是一张「路由卡」，不是一个状态标签**。`triage_only` 的存在本身就是「允许不做」的产品表态 —— 这是整个流程里最值得搬进原型的一处。

### 第 5 步 · 分支计划

```
## Branch Plan
- status: needs_approved_repo_context     base_branch: main     issue_branch: None
- repo_path_captured: False               execute_required_for_branch_claim: True
```

```bash
loopx issue-fix caller-repo-branch --repo-path <已批准路径> --base-branch main \
  --validation-command "<仓库原生命令>" [--execute]     # 默认 dry-run
```

边界写得很死：`caller-repo-branch` **不做外部评论、不建 PR、不合并** —— 本地分支准备与外部写操作是分离的。

### 第 6 步 · 补丁 + 验证（确定性固件）

```bash
loopx issue-fix acceptance-fixture --repo <label> --issue-ref issues_1
```

可**离线复跑**，实测输出：

```
- workspace_mode: temporary_fixture      destructive_git_used: False
## Validated Fix Artifact
- fix_artifact_ready: True               pr_review_packet_ready: True
- repro_before_passed: False             ← 修复前必须失败
- validation_after_passed: True          ← 修复后必须通过
```

**`repro_before_passed: False` 是关键设计**：强制「先复现失败，再修复通过」。→ 右栏「验证」区块必须是**两段式徽标**（复现 ✗ → 修复 ✓），不是单个 ✓。

### 第 7 步 · 评审包

```
## PR Review Packet Preview
- ready: False
- readiness_blockers:
  - approved_repo_context_missing   - branch_not_executed
  - validation_not_run              - repo_relative_changed_files_missing
- external_pr_created: False        merge_performed: False
```

**四个就绪阻断项是显式闸门** → 面板应展示**阻断项清单**，而不是一个灰按钮。

描述契约固定 8 段，**可直接当交付物面板模板**：① 动机 ② 改动思路 ③ 关键代码或伪代码 ④ 具体改动 ⑤ 修复后复现 ⑥ 验证（含诚实的通过/失败/跳过） ⑦ 对主干的风险与未覆盖 ⑧ 关联议题。

### 第 8 步 · PR 生命周期监视

```bash
loopx issue-fix pr-lifecycle --pr-ref pull_456          # 投射为四种走向之一
loopx issue-fix pr-gate-reconcile                       # 合并级人工门与紧凑状态调和
loopx issue-fix pr-review-ack                           # 持久化带精确绑定的 owner 确认回执
loopx issue-fix pr-review-reconcile                     # 需确认 + 终态观测才算完
loopx issue-fix reviewer-plan / reviewer-request        # 推荐 reviewer / 发起正式请求
loopx issue-fix reviewer-notification-drain             # 按状态桶逐条排空通知
```

```
- creates_per_pr_continuous_monitor_todo: False     ← 不为每个 PR 建 todo
- monitor_scope: lifecycle_state_bucket             ← 监控按「状态桶」
- external_notification_granularity: one_pr_per_message
- decisions: ['runnable_successor','monitor_continuation','user_gate','no_followup']
```

**监控粒度是状态桶而非每个 PR** —— 防 todo 爆炸的关键设计；四决策闭合 PR 之后的全部走向。

### 第 9 步 · 收口与资产沉淀

```bash
loopx issue-fix outcome --goal-id <id> --repo <l> --issue-ref issues_1
loopx issue-fix metrics --goal-id <id>
loopx issue-fix repository-memory-sync --goal-id <id>
```

`outcome` 是**状态投射**（不产生新事实）；`metrics` 输出**基线 / 可归属产出清单 / 仓库增量 / 缺失数据投射**；`repository-memory-sync` 把修复知识**沉淀为可复用资产**。

### 4.10 贯穿九步的四个治理原语

| 原语 | 命令 | 作用 | 原型承载 |
|---|---|---|---|
| **算力闸门** | `loopx quota should-run` | 决定下一轮跑不跑 | 卡片「可执行 / 暂停」态 |
| **所有权** | `loopx todo claim` · `loopx task-lease {acquire,renew,transfer,release,inspect}` | 谁拥有这个切片 | 卡片负责人 |
| **人工审批门** | `loopx operator-gate --decision {approve,defer,reject} --reason-summary <必填>` | 正式人工决策 + **必填理由** | 右栏「审批门」 |
| **证据账本** | `loopx evidence-log --goal-id <id> --agent-id <a> --thin` | 每 agent 的精简公开安全账本 | 右栏「Run Log」 |

`handoff-mode {show,set} --mode {legacy,soft_claim,hard_lease}`：修改**要求目标处于静止态**（无已认领的开放待办、无时间有效的租约）—— 这是一条**并发安全的产品约束**，原型改这个开关时应先做前置校验。

---

## 5. 字段驱动总表（细化原型的直接输入）

> 用法：先把这张表读成「**UI 元素清单**」，再回到画布找承载位。凡是画布上写死了文案的地方，都标记为待改。

### 5.1 目标级（goal）

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `goals[].status` | `active` / `paused` / `stopped` | 看板是否有内容 | 顶栏 |
| `adapter.status` | `connected` / … | 适配器健康点 | 顶栏 |
| `coordination.requires_parent_approval` | 动作类别数组 | **审批门拦哪几类动作** | 右栏审批门 |
| `coordination.write_scope` | 范围数组 | 允许写的范围 | 右栏审批门 |
| `execution_profile.cadence` | `bounded_progress_segment` | 节奏标签 | 右栏进度 |
| `execution_profile.must_include` | 三类产物 | **完成度清单** | 右栏进度/验证 |
| `execution_profile.spend_rule` | `spend_only_after_…` | 记账顺序提示 | 右栏成本 |
| `execution_profile.small_streak_threshold` | `2` | 连续小进展阈值 → 自愈触发 | 右栏自愈条 |

### 5.2 待办级（todo）

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `status` | `open` / `done` / `blocked` / `deferred` | **看板列** | 看板 |
| `role` | `user` / `agent` | 谁该做 | 看板卡 |
| `task_class` | `advancement_task` / `continuous_monitor` / `user_gate` / `user_action` / `blocker` | 卡片类型徽标 | 看板卡 |
| `claimed_by` | agent id | 负责人 | 看板卡 |
| `continuation_policy` | `independent_handoff` / `same_agent_non_delivery` | 能否换人续做 | 详情 |
| `successor_todo_id` / `unblocks_todo_id` | 待办 id | **依赖血缘（A 完成自动激活 B）** | 右栏 stepper |
| `resume_when` | 条件表达式 | 何时重新激活 | 详情 |
| `cadence` / `next_due_at` / `expires_at` | 时间 | 监视型卡片的时间维度 | 看板卡 |
| `monitor_target_key` | 状态桶 key | 同一桶合并显示 | 看板 |
| `blocks_agent` / `excluded_agent` | agent id 数组 | 谁不能做 | 详情 |
| `required_capability` / `target_capability` | 能力名 | **能力缺口** | 团队资产 / 右栏 |
| `capability_gap_status` | `found` / `fixed` / `real_callsite_verified` | 缺口修复进度 | 右栏 |
| `required_write_scope` | 范围 | 写范围 | 右栏 |
| `decision_scope` / `decision_outcome` | `approve` / `reject` / `cancel` | 决策类卡片 | 右栏审批门 |
| `validation_command` / `validation_label` | 命令 | 验证行 | 右栏验证 |
| `evidence` | 证据引用 | 证据账本条目 | 右栏 Run Log |

### 5.3 交接级（handoff）

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `handoff_readiness.ready` | `True` / `False` | 能否交接 | 右栏 |
| `handoff_readiness.codex_ready` | `True` / `False` | 宿主侧是否就绪 | 右栏 |
| `handoff_checks.pass[...]` / `fail[...]` | 5 项检查名 | **逐项检查清单** | 右栏 |
| `handoff_interface_budget.max_lines` / `max_chars` | `16` / `1800` | 交接包体积上限 | 右栏 |
| `handoff_state.status` | `ready_waiting_for_run` | 交接态 | 右栏 |
| `post_handoff_run_seen` | `True` / `False` | 交接后是否真的跑了 | 右栏 |

### 5.4 配额与队列

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `quota.state` | `operator_gate` / 正常 | **卡片可执行态** | 看板卡 |
| `quota.slots` | `0/1440` | 配额槽进度 | 右栏成本 |
| `quota.compute` | `1.0` | 权重 | 右栏成本 |
| `long_task_cadence_hint.signal` | `blocked` / … | 长任务是否卡住 | 右栏自愈条 |
| `long_task_cadence_hint.reasons` | 原因数组 | **卡住的原因（可解释）** | 右栏自愈条 |
| `orchestration.spawn_allowed` / `max_children` | 布尔 / 数字 | 能否派生并行 agent | 右栏 |
| `attention_queue.summary.items` | 数字 | 待处置计数 | 左栏 |
| `attention_queue.waiting_on` | `controller` / `agent` / `user` / `external` | **看板第三列判据** | 看板 |
| `attention_queue.severity` | `action` / `info` | 卡片醒目度 | 看板卡 |
| `attention_queue.source` | `active_state` / … | 来源标识 | 看板卡 |
| `asset_todos.user_open` / `agent_open` | 数字 | 人机待办配比 | 看板卡 |

---

## 6. 端到端时序（一屏速览）

> 左列为层归属：**[R]** = 能力供给面（Runtime）· **[T]** = 任务控制面（LoopX）

| T | 层 | 动作 | 命令 | 产出 | 原型承载 |
|---|---|---|---|---|---|
| T0 | [R] | 装载运行时能力 | `doctor` · `slash-commands --install` | 健康报告 + 宿主命令 | 设置·MCP（04） |
| T1 | [R] | 装载技能 | `workflow-skills --install` · `project-skill install` | 6 件技能 + 校验态 | 团队资产（02） |
| T2 | [T] | 建目标 | `connect` → `start-goal --guided` | `goal_start_contract` + `ordered_steps` | 新建任务（09） |
| T3 | [T] | 产生候选任务 | `todo suggest --from … --trigger …` | `todo_suggestion_prompt_v0`（**契约，非分析**） | 看板「待办」 |
| T4 | [T] | 同步状态 | `sync-global` · `refresh-state` · `goal-channel sync` | 注册表合并 + 外部看板投射 | 看板四列 + 顶栏 |
| T5 | [T] | 元数据进场 | `issue-fix workflow-plan --fetch-metadata` | 工作流计划包 | 详情「来源」行 |
| T6 | [T] | 补仓库上下文 | `--repository-context-json`（5 方面） | `unresolved_required_aspects: []` | 右栏「证据」 |
| T7 | [T] | 候选预检 | 同上包 | `next_safe_action` | 右栏「下一步」 |
| T8 | [T] | 算力闸门 | `quota should-run` | `eligible` / `wait` | 卡片「可执行」态 |
| T9 | [T] | 领任务 | `todo claim` · `task-lease acquire` | `claimed_by` + 租约 | 卡片负责人 |
| T10 | [T] | 分诊 | `issue-fix feasibility` | 三路由其一 | **右栏路由卡** |
| T11 | [T] | 开分支 | `caller-repo-branch --execute` | 议题分支 + 验证命令绑定 | 右栏「交接」 |
| T12 | [T] | 复现失败 | 固件 `repro_smoke` | `repro_before_passed: False` | 验证徽标①✗ |
| T13 | [T] | 补丁 | 最小补丁 | `patch_file` | 变更 diff |
| T14 | [T] | 验证通过 | 固件 `validation` | `validation_after_passed: True` | 验证徽标②✓ |
| T15 | [T] | 组评审包 | `pr-review` 系列 | 8 段描述 + 阻断项清单 | 交付物面板 |
| T16 | [T] | 人工审批门 | `operator-gate --decision … --reason-summary` | 决策 + 理由 | 右栏「审批门」 |
| T17 | [T] | 监视 PR | `pr-lifecycle` · `pr-review-reconcile` | 四决策之一 | 看板卡片状态 |
| T18 | [T] | 记账 | `quota spend-slot` | `spent_slots` | 右栏「成本/预算」 |
| T19 | [T] | 沉淀 | `repository-memory-sync` · `metrics` | 可复用修复知识 + 增量 | 团队资产（02） |
| T20 | [T] | 自愈（异常时） | `self-repair` 五步 | 最低层持久修复 | 右栏「Run Log」 |

---

## 7. 自愈回路（异常分支）

`loopx-self-repair` 的五步：

1. **暂停投递** —— 在控制面事实解释清楚「为什么这活儿有效」之前，**不花配额、不继续适配器工作**；
2. **建紧凑证据包** —— `git status --short --branch` + `diagnose` / `status` / `quota should-run` / `history`（全部 `--format json`）；
3. **分类失败** —— 对照 `references/repair-patterns.md` 的已知模式；
4. **归属责任层** —— 五选一：agent 行为失误 / 状态投射或配额负载缺陷 / 活跃状态撰写缺口 / 基准与产品路径错位 / 文档流程卫生；
5. **在最低的持久层修复**（修根因，不是打补丁）。

**触发信号**（可直接当原型告警文案）：任务进展异常小 · 跟随陈旧或矛盾的建议动作 · 跳过更高优先级的阻塞项去做兜底工作 · 报告含糊的负责人/用户门 · 丢失待办投射 · 把临时产物混进提交。

→ 右栏加**「自愈」告警条**（琥珀色，仅异常时出现），显示当前步 + 归属层。现在完全没有。

---

## 8. 设计点（按层标注）

### P0 — 直接补流程缺口

| # | 设计点 | 层 | 承载位置 | 依据 |
|---|---|---|---|---|
| 1 | **三路由分诊卡**（`fix_pr` / `comment_only` / `triage_only`） | [T] | 右栏新增区块 | §4 第 4 步 |
| 2 | **两段式验证徽标**（复现✗ → 修复✓） | [T] | 右栏「证据/验证」 | §4 第 6 步 |
| 3 | **就绪阻断项清单**（4 项） | [T] | 交付物面板 | §4 第 7 步 |
| 4 | **描述 8 段契约** | [T] | 交付物面板模板 | §4 第 7 步 |
| 5 | **看板四列字段驱动** | [T] | 看板（01） | §3.5 |
| 6 | **运行时接入分组**（19 种 runtime 枚举） | [R] | 设置·MCP（04） | §2.1 |

### P1 — 补语义深度

| # | 设计点 | 层 | 承载位置 | 依据 |
|---|---|---|---|---|
| 7 | 卡片「来源」芯片（7 个来源） | [T] | 看板卡 | §3.2 |
| 8 | 配额闸门态（可执行 / 暂停）+ 卡住原因 | [T] | 看板卡 | §5.4 |
| 9 | 负责人 + 租约态 | [T] | 看板卡 | §5.2 |
| 10 | 依赖血缘（`successor` / `unblocks`） | [T] | 右栏 stepper | §5.2 |
| 11 | **能力缺口提示**（需求 − 供给） | [R]↔[T] | 看板卡 + 右栏 | §2.3 |
| 12 | 资产健康徽标 + **「按 runtime」作用域** | [R] | 团队资产（02） | §2.1/2.4 |
| 13 | 自愈告警条（五步 + 归属层） | [T] | 右栏 | §7 |
| 14 | 顶栏同步指示（上次同步 + 注册表健康） | [T] | 顶栏 | §3.3 |

### P2 — 增强可信度

| # | 设计点 | 层 | 承载位置 |
|---|---|---|---|
| 15 | 审批门读 `requires_parent_approval` 字段 | [T] | 右栏「审批门」 |
| 16 | 「已启用 / 已修改」区分 | [R] | 团队资产（02） |
| 17 | 产出度量（`outcome` / `metrics`） | [T] | 右栏「成本/预算」 |
| 18 | 公私边界可见（public / private 标签） | [T] | 详情「来源」行 |
| 19 | 上下文证据可信度（`trust` / `freshness`） | [T] | 右栏「证据」 |

---

## 9. 命名规范（中文为主）

**规则**：

1. 正文首次出现：**中文名（English）**；其后只用中文名。例：「审批门（gate）」「分诊（feasibility）」；
2. **命令、字段名、枚举值一律保持原样**（必须可复跑），不做翻译；
3. 分诊路由 `fix_pr` / `comment_only` / `triage_only` 作为**枚举值**保留英文，但 UI 展示用中文：**「备修复」/「仅评论」/「仅记录」**；
4. 全部术语的中文首选名与白话解释，统一维护在 **`docs/glossary.md`**（含「循环治理术语」一节），本文不重复定义；

**高频术语速查**（详见术语表）：

| 英文 | 中文首选 | 一句话白话 |
|---|---|---|
| goal | 目标 | 一件长期要做成的事 |
| todo | 待办 | 目标下面的一步 |
| slice | 切片 | 一次能做完并验证的一小块 |
| gate | 审批门 | 必须人点头才能继续的关卡 |
| quota | 算力配额 | 还能跑几轮 |
| lease | 租约 | 这一步现在归谁做，有期限 |
| handoff | 交接 | 把任务交给下一轮/下一个人 |
| packet | 契约包 | 系统给的、机器可读的指令与约束 |
| fixture | 固化样本 | 可离线复跑的验收样例 |
| readiness blocker | 就绪阻断项 | 还差哪几项才能交付 |
| capability gap | 能力缺口 | 任务要的能力当前不具备 |
| repro / validation | 复现 / 验证 | 先跑出失败，再证明修好了 |

---

## 10. 与前序文档的关系 / 下一步

| 文档 | 层次 | 关系 |
|---|---|---|
| `docs/research/competitive-intel-huangruiteng-loopx.md` | 认知层 | 本文把它的「Issue-Fix Capability」一行展开成可执行流程 |
| `docs/decisions/loop-management-optimization.md` | 建议层 | 本文为其 B（目标契约）/ C（真审批门）/ E（证据化验收）/ G（自主重规划）补上字段 |
| `docs/glossary.md` | **术语层** | 本文所有专有名词的权威中文释义 |
| 本文 | 流程层 | 输出 §8 的 19 个设计点 |
| `docs/design-system/frontend-vs-prd-audit.md` | 实现层 | §8 的 P0 六项并入该审计的「缺失」清单 |

**待确认**：

1. 是否把 §8 的 P0 六项落到主画布 `724693301521075`（画布定稿后再 1:1 同步 `frontend/`，保持画布为唯一事实源）；
2. `coordination.requires_parent_approval` 与 `execution_profile.must_include` 是否进 LoopDesk 的 `LOOP-STATE.json`（目前 `safety.denylist` 语义与之不匹配）；
3. **能力供给面（Runtime）需要补一份独立事实源** —— 本文只固定了交界字段；「团队资产」「设置·MCP」的完整设计依据应来自 Runtime 的能力模型。

---

### 附录 A · 本文用到的 LoopX 命令（1.0.2 可复跑）

```bash
# ── [R] 能力供给面（Runtime 交界）
loopx doctor
loopx agent-onboard --agent-type <t> --project . [--available-capability <c>]
loopx agent-onboard --list-agent-types
loopx slash-commands --install --surface <host> [--dry-run]
loopx workflow-skills [--install | --uninstall] [--skills-dir <dir>] [--dry-run]
loopx project-skill {status|install|uninstall} --skill <n> --surface {codex|claude-code|opencode|pi}
loopx connector {list|rank|register|use}          # 数据连接器注册表（非 MCP 服务）
loopx ready-score --goal-id <id>

# ── [T] 任务控制面
loopx status ; loopx dashboard ; loopx diagnose --goal-id <id>
loopx connect --project . ; loopx start-goal --guided --project . --goal-text "<g>"
loopx todo {add|list|claim|update|complete|supersede|archive-completed|suggest|capture-followups|project-markdown}
loopx todo suggest --goal-id <id> --from <src> --trigger <trig> --limit <n>
loopx task-lease {acquire|renew|transfer|release|inspect} --goal-id <id> --todo-id <t>
loopx quota {status|plan|should-run|spend-slot|void-slot|monitor-poll} --goal-id <id>
loopx operator-gate --goal-id <id> --decision {approve|defer|reject} --reason-summary <s>
loopx evidence-log --goal-id <id> --agent-id <a> --thin
loopx handoff-mode {show|set} --goal-id <id> [--mode {legacy|soft_claim|hard_lease}]
loopx sync-global [--dry-run] [--replace-state] ; loopx refresh-state --goal-id <id>
loopx goal-channel {setup|attach|sync|doctor|notify-gate} --goal-id <id>
loopx review-packet --goal-id <id> ; loopx history --goal-id <id>
loopx machine-config {describe|preview|apply|inspect|remove|rollback}

# ── issue-fix（21 个子命令，流程主线用前 8 个）
loopx issue-fix workflow-plan --url <url> --fetch-metadata --format json
loopx issue-fix feasibility --reproduction-status <s> --scope-class <c> --goal-id <id>
loopx issue-fix caller-repo-branch --repo-path <p> --base-branch main [--execute]
loopx issue-fix acceptance-fixture --repo <l> --issue-ref issues_1
loopx issue-fix pr-lifecycle --goal-id <id> --pr-ref pull_456
loopx issue-fix pr-gate-reconcile ; loopx issue-fix pr-review-ack
loopx issue-fix pr-review-reconcile ; loopx issue-fix pr-review-reconcile-acked
loopx issue-fix outcome --goal-id <id> ; loopx issue-fix metrics --goal-id <id>
loopx issue-fix repository-memory-sync --goal-id <id>
```

### 附录 B · 1.0.2 的 issue-fix 子命令全表（21 项）

| 子命令 | 用途 |
|---|---|
| `workflow-plan` | 从公开元数据规划完整工作流到有序待办 / 验证 / 评审包就绪 |
| `feasibility` | 从紧凑公开观测中**恰好选一条**路由 |
| `pr-lifecycle` | 把 PR 生命周期观测投射为四类走向之一 |
| `pr-gate-reconcile` | 通知 owner 前调和「合并级人工门」与紧凑 PR 状态 |
| `pr-review-reconcile` / `pr-review-reconcile-acked` | 仅在 owner 确认 + 终态观测后完成评审类 user_action |
| `pr-review-ack` | 持久化带精确绑定的 owner 确认回执 |
| `outcome` | 组合公开安全的状态/产出投射 |
| `metrics` / `metrics-supplement` | 基线 / 可归属产出清单 / 仓库增量 / 缺失数据 |
| `repository-memory-sync` | 通过可复用上下文提供模块做有界同步 |
| `repository-snapshot` | 采集紧凑 GitHub 仓库快照 |
| `reviewer-plan` / `reviewer-request` | 从 owner 证据推荐评审者 / 发起正式请求 |
| `reviewer-notification-drain` | 按状态桶逐条排空评审通知 |
| `reviewer-feedback-inbox` | 排空或确认评审组的事件收件箱 |
| `promote-discovered-issue` | 为 agent 发现的缺陷建/复用规范议题 |
| `acceptance-fixture` / `repo-branch-fixture` / `caller-repo-branch` | 三种确定性修复回路（离线 / 临时 git / 调用方仓库） |

### 附录 C · 三组最容易混淆的概念（务必切开）

| 概念 A | 概念 B | 区别 |
|---|---|---|
| **LoopX 数据连接器**（`loopx connector list`） | **Runtime 的 MCP 服务** | 前者是 LoopX 自己的 provider 注册表（含 `layer` / `value` / `score` 排序，实测为示例数据）；后者是 Agent Runtime 的工具服务配置。**二者没有从属关系** |
| **LoopX 技能文件**（`loopx-*`，LoopX 投递） | **Runtime 的技能体系**（发现/加载/优先级） | LoopX 只写自己的受管文件，不拥有技能体系 |
| **审批门（gate）** | **权限配置（permission profile）** | 前者是「这一步要不要人点头」的任务级关卡；后者是「这个 agent 有多大权限」的运行级姿态 |

### 附录 D · 本机实测路径

| 项 | 路径 |
|---|---|
| CLI | `/opt/homebrew/bin/loopx` → `~/.local/share/loopx-venv/bin/loopx`（版本 `loopx 1.0.2`） |
| 项目状态 | `<repo>/.loopx/registry.json`、`<repo>/.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md` |
| 全局真源 | `~/.codex/loopx/registry.global.json`（运行时根 `~/.codex/loopx/`） |
| LoopX 受管技能 | `~/.codex/skills/loopx-{project,pr-review,pr-program,self-repair,doc-registry,benchmark}/SKILL.md` |
