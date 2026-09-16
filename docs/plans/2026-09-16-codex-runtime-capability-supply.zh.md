# Codex 运行时 · 能力供给面（原型设计输入）

> **Status** v1.0 · 2026-09-16 · **所有者** 产品/设计
> **目标运行时** Codex —— 本机 `codex-cli 0.146.0`（`~/.local/bin/codex` → `~/.codex/packages/standalone/current/bin/codex`）
> **控制面** LoopX 1.0.2（`/opt/homebrew/bin/loopx` → `~/.local/share/loopx-venv/bin/loopx`）
> **事实来源** 全部实机跑出：`codex doctor` / `codex mcp list` / `codex plugin list` / `codex plugin marketplace list` / `codex features list` / `loopx agent-onboard --agent-type codex-cli`。**不引用 README、博客或旧笔记。**
> **配套** 流程层同目录 `2026-09-16-issue-fix-end-to-end-flow.zh.md`；术语层 `docs/glossary.md`
> **用途** 为原型三页——**设置·Agent（画布 03）/ 设置·MCP（画布 04）/ 团队资产（画布 02）**——提供字段级依据

---

## 0. 本文的范围

控制面（LoopX）回答「**该干什么、干到哪、能不能干**」；能力供给面（运行时）回答「**谁来干、会什么、拿什么工具**」。

| | L1 任务控制面 | L2 能力供给面（本文） |
|---|---|---|
| 系统 | LoopX | **Codex** |
| 持有 | 目标 / 待办 / 状态 / 证据 / 配额 / 租约 / 审批门 | 运行时宿主面 / 技能装载 / MCP 服务 / 插件 / 权限配置 |
| 权威结论 | 见流程文档 | **本文** |

**边界声明**：本文对 **Codex 侧**给权威结论（实机取证）。对 LoopX 侧**只写它要求 Codex 提供什么**（交界），不重复流程文档的内容。

**本文不含**：Codex 的模型/推理参数调优、会话记录格式、上下文压缩策略——这些不影响当前原型的界面结构。

---

## 1. Codex 的四张清单（决定 L2 的信息架构）

运行时这一侧不是一个「配置页」，而是**四张彼此独立的清单**，各有自己的所有者与生命周期：

| # | 清单 | 权威命令 | 管什么 | 变更频率 | 原型承载 |
|---|---|---|---|---|---|
| 1 | **运行时宿主面** | `loopx agent-onboard --list-agent-types` | 谁在跑这个循环 | 项目级，罕见 | 设置·Agent（03） |
| 2 | **MCP 服务** | `codex mcp list` | 能调哪些外部工具 | 周级 | 设置·MCP（04） |
| 3 | **插件与市场** | `codex plugin list` · `codex plugin marketplace list` | 官方扩展包 | 月级 | 设置·MCP（04） |
| 4 | **技能** | `~/.codex/skills/` + `.loopx-skill-install.json` | 会哪些流程 | 周级 | 团队资产（02） |

> **设计含义**：现在原型「设置·MCP」只有一类卡片（外部系统），把四张清单里的两张压成了一张。**必须拆成三组**：运行时接入 / MCP 服务 / 插件与市场。技能归团队资产。

---

## 2. 运行时宿主面：四个 Codex 面（受约束选择器）

LoopX **拒绝**裸 `codex`——因为四个宿主面的循环激活路径完全不同。

| `agent_type` | 宿主循环 | 入口 | 本机证据 |
|---|---|---|---|
| `codex-cli` | 可见的 Codex CLI `/goal` | `$loopx <task>` 或 `/skills` 里的 LoopX 技能 | `~/.codex/skills/` 已装（`CODEX_HOME/skills` 是 LoopX 的默认投递目标） |
| `codex-app` | Codex App 心跳自动化 | 同上 | `config.toml` 有 `[desktop]` 段；`[plugins."codex-app-tools@openai-bundled"] enabled` |
| `codex-app-ssh` | SSH 下不可用自动化时的可见 App `/goal` | 同上 | — |
| `codex-ide-plugin` | 可见的 Codex IDE 插件 `/goal` | 同上 | rollout 来源实测 `vscode=197`（占比最高） |

**歧义值处理**（原文）：
```
Ambiguous inputs:
- `codex`       -> use one of `codex-app`, `codex-app-ssh`, `codex-ide-plugin`, `codex-cli`
- `openai-codex`-> use one of ...
- `cli`         -> use one of `codex-cli`, `manual`, `other-agent`
```

> **设计点（P0）**：运行时选择器必须是**受约束选择器**（枚举），不能是自由文本 —— 用户输入 `codex` 会被控制面拒绝。当输入落到歧义值时要给「**四选一**」的选择态，而不是报错。
> **默认值**：LoopX 的技能投递默认根就是 `CODEX_HOME/skills`，故本原型**默认 `codex-cli`**，同族其余三个作为可选项。

---

## 3. MCP 服务：两张表 × 两个来源

### 3.1 命令面

```
codex mcp { list | get | add | remove | login | logout }
```

### 3.2 `codex mcp list` 输出**两张表**

| 表 | 列 |
|---|---|
| **stdio 服务** | `Name` · `Command` · `Args` · `Env` · `Cwd` · `Status` · `Auth` |
| **HTTP 服务** | `Name` · `Url` · `Bearer Token Env Var` · `Status` · `Auth` |

- `Status` ∈ `enabled` / `disabled`
- `Auth` ∈ `Unsupported` / `Bearer token`（HTTP 表实测值）
- **`Env` 值在 CLI 输出里已被脱敏为 `*****`** —— UI 不得尝试还原明文

### 3.3 实测本机（6 条，其中 config 直配 3 条）

| 名称 | 类型 | 来源 | Status |
|---|---|---|---|
| `codex_app` | stdio | **插件携带**（`openai-bundled/codex-app-tools`） | disabled |
| `computer-use` | stdio | config 直配 | disabled |
| `cua_repl` | stdio | **插件携带**（`openai-bundled`） | enabled |
| `node_repl` | stdio | config 直配 | enabled |
| `pencil` | stdio | config 直配 | enabled |
| `github` | **HTTP** | config（`Bearer Token Env Var = GITHUB_PERSONAL_ACCESS_TOKEN`） | enabled |

`codex doctor` 的 Configuration 段交叉印证：`mcp → 3 server (3 stdio) · 1 disabled`（**doctor 只数 config 直配的 3 条**）。

### 3.4 配置落点

```toml
# ~/.codex/config.toml
[mcp_servers.<name>]
command = "..."          # stdio
args    = ["..."]
cwd     = "."
enabled = false
startup_timeout_sec = 120
[mcp_servers.<name>.env]
KEY = "value"            # UI 里必须脱敏
```

> **设计点（P0）**：MCP 卡片必须能区分「**你配的**」与「**插件带的**」，并且这两类**不能同权删改**——插件携带的条目随插件升级而变。当前原型完全没有这一维。

---

## 4. 插件与市场

```
codex plugin  { add | list | remove }
codex plugin marketplace { add | list | upgrade | remove }
```

配置落点：

```toml
[marketplaces.<name>]
source_type = "local"        # 实测值：local（也支持 Git）
source      = "/abs/path"

[plugins."<name>@<marketplace>"]
enabled = true
```

实测本机 **4 个市场 / 11 个已启用插件**（`github@openai-api-curated`、`visualize@openai-bundled`、`documents|pdf|spreadsheets|presentations|template-creator@openai-primary-runtime`、`browser|chrome|codex-app-tools|unified-computer-use|computer-use@openai-bundled`）。

### 4.1 实测健康失败（真实的、可复现）

```
$ codex plugin list
Error: failed to load configured marketplace snapshot(s):
- `openai-curated`     at …/.codex/.tmp/plugins: marketplace root does not contain a supported manifest
- `openai-api-curated` at …/.codex/.tmp/plugins: marketplace root does not contain a supported manifest
```

两个市场的 manifest 缺失，导致 **`plugin list` 与 `marketplace list` 双双整体失败** —— 而 `config.toml` 里 `github@openai-api-curated` 正指向坏市场。

> **设计点（P0）**：市场健康必须**逐条**呈现（每条给 `marketplace root does not contain a supported manifest` 这类原文原因），**一个坏了不能拖垮整页**。这是「资产健康徽标」最硬的真实素材。

---

## 5. 技能：目录 + 控制面投递清单

### 5.1 三个来源

| 来源 | 位置 | 实测数量 | 说明 |
|---|---|---|---|
| **内置** | `~/.codex/skills/.system/` | 6 | `imagegen` / `openai-docs` / `plugin-creator` / `review-agent` / `skill-creator` / `skill-installer`（含 `.codex-system-skills.marker`） |
| **控制面投递** | `~/.codex/skills/loopx*` | 6 | `loopx` / `loopx-doc-registry` / `loopx-pr-program` / `loopx-pr-review` / `loopx-project` / `loopx-self-repair` |
| **用户自建** | `~/.codex/skills/<任意>` | 2+ | 实测 `huashu-design` / `zread-skill` |

技能结构：`SKILL.md`（含 YAML frontmatter `name` / `description`）+ 可选 `agents/openai.yaml`。

### 5.2 控制面投递清单（L1 → L2 的交接凭据）

`~/.codex/skills/.loopx-skill-install.json`，`schema_version: loopx_skill_install_readback_v0`：

| 字段 | 实测值 | 驱动的 UI |
|---|---|---|
| `installed_at` | `2026-08-22T03:57:01+00:00` | 技能包「安装于」 |
| `owner` | `loopx_workflow_skills_cli` | 归属标签（谁装的） |
| `integration_mode` | `python_distribution_cli` | 集成方式 |
| `materialized_skill_ids` | 6 个 id | 已落地清单 |
| `skills.digest` | `20cb307f…` | **整包指纹** |
| `skills.items.<id>.available` | `true` | 可用性 |
| `skills.items.<id>.file_count` | `1` / `2` / `4` / `5` | 文件数 |
| `skills.items.<id>.sha256` | 逐技能哈希 | **完整性校验** |
| `source.kind` | `python_distribution` | 来源类型 |
| `source.revision` | `0.5.0` | ⚠️ **包版本（落后于控制面 1.0.2）** |
| `source.revision_kind` | `package_version` | 版本语义 |
| `source.git_dirty` | `false` | 来源是否脏 |

同目录另有 `.loopx-workflow-skills.lock`（空文件，锁标记）。

### 5.3 投递契约（控制面侧声明，`loopx agent-onboard` 返回）

```
skill_delivery.schema_version = loopx_host_skill_delivery_v0
skill_delivery.mode           = surface_managed
skill_delivery.owner          = loopx_surface_installer
skill_delivery.codex_skills_root_required = true
skill_delivery.host_readback_required     = false
skill_delivery.active_project_skill_ids   = []
```

### 5.4 实测健康失败（真实的、可复现）

```
$ loopx project-skill status --skill loopx-project --project .
- status: blocked
- error: project skill scope marker is missing:
         ~/.local/share/loopx-venv/…/site-packages/skills/loopx-project/.loopx-skill-scope
```

**6 件投递技能中抽查 3 件，3 件全部 `blocked`** —— 作用域标记文件缺失。

> **设计点（P0）**：技能卡必须有**三态来源**（内置 / 控制面投递 / 用户自建）+ **三类健康检查**：
> ① `sha256` 与清单一致？（被改动过）
> ② 作用域标记存在？（`blocked` 的真实原因）
> ③ `source.revision` 与控制面版本对齐？（实测 0.5.0 ≠ 1.0.2）
> 现在团队资产卡只有名称与描述，这三类都无处显示。

---

## 6. 命令门面与运行级权限

### 6.1 命令门面（slash commands）

```
loopx slash-commands [--install | --uninstall] --surface <15 个值> [--dry-run]
```

`--surface` 枚举：`all, codex, codex-cli, codex-app, codex-app-ssh, codex-ide-plugin, codex-ide, claude-code, opencode, gemini, gemini-cli, cursor, cursor-agent, zcode, z-code, agy, antigravity, pi`

相关命令（同一族）：
```
loopx workflow-skills [--install | --uninstall] [--skills-dir <dir>] [--dry-run]
  --skills-dir 默认 CODEX_HOME/skills 或 ~/.codex/skills   ← Codex 是默认投递目标

loopx machine-config { describe | preview | apply | inspect | remove | rollback }
  preview 返回 plan revision，apply 必须带回该 revision   ← 机器级变更的通用四阶段协议
```

### 6.2 运行级权限（**不是**任务级审批门）

`codex doctor` 的 Configuration → `sandbox` 节：

| 字段 | 实测值 |
|---|---|
| `approval policy` | `OnRequest` |
| `filesystem sandbox` | `restricted` |
| `network sandbox` | `restricted` |
| `linux helper` | `none` |
| `execve wrapper helper` | `~/.codex/tmp/arg0/…/codex-execve-wrapper` |

### 6.3 能力开关

```
codex features { list | enable | disable }
```

`codex features list` 三列：`name` · `stage` · `enabled`。`stage` ∈ `stable` / `under development` / `removed`。
实测：**38 个已启用 · 0 个被覆盖**（`doctor` 的 `feature flags` 行）。本机 `[features] goals = true, js_repl = false`。

> **设计点（P0）**：**权限配置（运行级）≠ 审批门（任务级）**。前者是「这台机器允许这个 agent 做什么」，归**设置·Agent**；后者是「这一个任务要不要人点头」，归**右栏审批门**。两者同名易混，UI 上必须分开且各自标明归属。

---

## 7. 健康巡检：`codex doctor` 的七个分区

`codex doctor [--json | --summary | --all | --no-color]` —— **`--json` 输出脱敏的机器可读报告**，是直接可消费的字段源。

| 分区 | 子项 |
|---|---|
| Notes | `updates` · 告警 |
| Environment | `system` · `runtime` · `install` · `search` · `git` · `terminal` · `title` · `state` · `threads` |
| Configuration | `config` · `auth` · `mcp` · `sandbox` |
| Updates | `startup update check` · `update action` · `cached latest version` · `last checked at` · `latest version` · `latest version status` |
| Connectivity | `network` · `websocket` · `reachability` |
| Background Server | `app-server` · `daemon state dir` · `pid file` |

状态标记三档（原文符号）：`✓` 正常 · `⚠` 警告 · `○` 未运行/未知。

### 7.1 三类实测真实健康信号

| 类型 | 实测原文 | 严重度 |
|---|---|---|
| **版本漂移** | `0.154.0 available (current 0.146.0)` | ⚠ 警告（可升级） |
| **状态库陈旧行** | `state DB rows point at missing or unusable rollout files`；`rollout DB stale rows 2` | ⚠ 警告 |
| **市场 manifest 缺失** | `marketplace root does not contain a supported manifest` ×2 | 错误（整页失败） |

### 7.2 状态库落点（UI 不需要暴露，但影响「同步指示」语义）

| 库 | 路径 | 实测 |
|---|---|---|
| state DB | `~/.codex/state_5.sqlite` | integrity ok |
| log DB | `~/.codex/logs_2.sqlite` | integrity ok |
| goals DB | `~/.codex/goals_1.sqlite` | integrity ok |
| memories DB | `~/.codex/memories_1.sqlite` | integrity ok |
| thread history DB | `~/.codex/thread_history_1.sqlite` | ok |
| active rollouts | `~/.codex/sessions/**/*.jsonl` | **209 文件 · 263.53 MB** |

> **设计点（P0）**：`doctor` 的**分区即 UI 分区**，三档标记直接映射徽标。当前原型的设置页没有任何巡检视图。

---

## 8. 宿主循环激活：六步 + 三条成功判据 + 一条不可自动化边界 ★

这是 L1↔L2 交界上**最需要在 UI 上表达清楚**的一块。`loopx agent-onboard --agent-type codex-cli` 返回：

```
host_loop_activation.schema_version      = loopx_host_loop_activation_v1
host_loop_activation.host_surface        = codex_cli_visible_goal_mode
host_loop_activation.activation_method   = register_fresh_agent_or_explicit_takeover_before_host_loop_activation
host_loop_activation.activation_required_after_todo_write = true
```

### 8.1 身份闸门（`identity_selection_gate`）

| 字段 | 实测值 |
|---|---|
| `state` | `fresh_agent_registration_required` |
| `activation_allowed` | `false` |
| `action_required` | `true` |
| `default_action` | `register_fresh_agent` |
| `required_cli_arg` | `--agent-id <freshly-registered-agent-id>` |
| `preview_command` | `loopx register-agent --goal-id <g> --agent-id '<id>' --require-new` |
| `execute_command` | 同上 `+ --execute` |
| `external_write_required` | `true` |

**`continuation_contract`**（原文要求）：只有当执行结果同时满足
`ok=true` · `changed=true` · `written=true` · `global_sync.ok=true` · `registration_readback.verified=true`
才允许继续，然后**带着新 `--agent-id` 重跑 onboarding**，之后才写回待办或激活宿主循环。原文：*"treat preview as advisory"*。

### 8.2 `host_mutation` —— 不可自动化边界

```
host_mutation.owner                  = "Codex CLI TUI"
host_mutation.host_command           = "/goal <task_body>"
host_mutation.cli_can_mutate_directly = false
host_mutation.missing_host_tool_gate  = "Current session cannot set Codex CLI TUI /goal;
                                         show the exact `/goal <task_body>` text for the user to paste."
```

> **设计点（P0，本文独有）**：**控制面无法直接改变宿主状态**。UI 必须有一块「**待宿主操作**」卡：显示原文命令 + 一键复制 + 明确「本系统不会自动执行」。没有这块，用户会以为点了「开始」任务就自动跑起来了。

### 8.3 激活六步（原文）

1. 默认从身份闸门**注册一个新的、public-safe 的 agent id**；
2. 仅当用户**明确要求接管某个特定 agent** 时才复用已有身份；
3. 带着选定的 `--agent-id` **重跑 onboarding**；
4. 从 JSON 载荷读取 `task_body`；
5. 把可见的 Codex CLI TUI goal 设为 **`/goal <task_body>`**；
6. **保持投递在可见任务里，不要切到隐藏的无头执行。**

### 8.4 三条成功判据（原文）

1. 已选定一个新的已注册 agent 身份，或已记录精确的接管意图；
2. 可见的 Codex CLI TUI 已为本目标激活 `/goal <task_body>`；
3. 后续目标轮次都先经过 LoopX 的 quota / status / state，再进入交付工作。

### 8.5 节奏与成本模型（决定「什么时候刷什么」）

```
status_probe_policy.check_once_during_onboarding        = true
status_probe_policy.cheap_recheck_on_loopx              = 仅当激活缺失/未知/陈旧或 agent 新装时
status_probe_policy.do_not_recompute_every_loopx_turn   = true

cost_model.onboarding    = 安装/连接时跑一次，或宿主循环缺失/陈旧时
cost_model.loopx_task_start = `/loopx <task>` 或技能仅在 host_loop_activation 缺失/未知/陈旧/类型变更时调用
cost_model.normal_ticks  = 直接读 quota / status / state，不要每轮重算 onboarding
```

> **设计点（P1）**：顶栏「同步指示」不是「每秒轮询」，而是**一次性 + 廉价复检**。文案要说清「上次同步 / 下一次复检条件」，不要做成假实时。

---

## 9. 字段驱动总表 ★

> 读法：先把这张表当成 **UI 元素清单**，再回画布找承载位。凡画布上写死文案的地方，都标记为待改。

### 9.1 运行时宿主面

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `agent_type` | `codex-cli` / `codex-app` / `codex-app-ssh` / `codex-ide-plugin` / `claude-code` / `opencode` / `pi` / `manual` / `other-agent` | **运行时选择器（受约束）** | 设置·Agent（03） |
| 歧义输入 | `codex` / `openai-codex` / `cli` | 四选一的**消歧态** | 设置·Agent（03） |
| `host_surface` | `codex_cli_visible_goal_mode` | 宿主面标签 | 设置·Agent（03） |
| `entry_command_hint` | `$loopx <task> or the explicit LoopX skill from /skills` | 入口提示 | 设置·Agent（03） |
| `activation_method` | `register_fresh_agent_or_explicit_takeover_before_host_loop_activation` | 激活方式说明 | 设置·Agent（03） |

### 9.2 身份与激活

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `identity_selection_gate.state` | `fresh_agent_registration_required` / 已选 | 身份闸门态 | 右栏 / 详情 |
| `identity_selection_gate.activation_allowed` | `true` / `false` | **「开始」是否可点** | 右栏 / 详情 |
| `identity_selection_gate.required_cli_arg` | `--agent-id <…>` | 待补参数提示 | 右栏 / 详情 |
| `preview_command` / `execute_command` | 命令原文 | **两段式确认（预览→执行）** | 右栏 / 详情 |
| `continuation_contract.required_result.*` | 5 个布尔 | **读回校验清单**（逐项打勾） | 右栏 / 详情 |
| `host_mutation.cli_can_mutate_directly` | `false` | **「待宿主操作」卡是否出现** | 右栏 / 详情 |
| `host_mutation.host_command` | `/goal <task_body>` | **可复制命令文本** | 右栏 / 详情 |
| `host_mutation.missing_host_tool_gate` | 原文说明 | 门禁原因（灰字） | 右栏 / 详情 |
| `activation_required_after_todo_write` | `true` | 写回后强制跳激活 | 右栏 / 详情 |

### 9.3 MCP 服务

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| 表类型 | `stdio` / `http` | **两段列表**（字段不同） | 设置·MCP（04） |
| `Name` | 字符串 | 服务名 | 设置·MCP（04） |
| `Command` / `Args` / `Cwd` | 字符串 | stdio 行明细 | 设置·MCP（04） |
| `Url` | URL | http 行明细 | 设置·MCP（04） |
| `Env` | 已脱敏 `*****` | 环境变量（**只读脱敏**） | 设置·MCP（04） |
| `Bearer Token Env Var` | `GITHUB_PERSONAL_ACCESS_TOKEN` | **凭据变量名**（非值） | 设置·MCP（04） |
| `Status` | `enabled` / `disabled` | 开关 + 卡片禁用态 | 设置·MCP（04） |
| `Auth` | `Unsupported` / `Bearer token` | 鉴权徽标 | 设置·MCP（04） |
| 来源 | config 直配 / **插件携带** | **来源芯片 + 可删改性** | 设置·MCP（04） |

### 9.4 插件与市场

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| `[marketplaces].source_type` | `local` / `git` | 市场来源标签 | 设置·MCP（04） |
| `[marketplaces].source` | 路径 | 市场根路径 | 设置·MCP（04） |
| 市场加载结果 | ok / `marketplace root does not contain a supported manifest` | **逐条健康徽标 + 原文原因** | 设置·MCP（04） |
| `[plugins."<n>@<m>"].enabled` | `true` / `false` | 插件开关 | 设置·MCP（04） |

### 9.5 技能（团队资产）

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| 来源 | 内置 `.system` / 控制面投递 / 用户自建 | **来源分组 + 芯片** | 团队资产（02） |
| `materialized_skill_ids` | 6 个 id | 已落地清单 | 团队资产（02） |
| `skills.items.<id>.sha256` | 哈希 | **完整性徽标**（被改动过） | 团队资产（02） |
| `skills.items.<id>.file_count` | 数字 | 文件数 | 团队资产（02） |
| `skills.items.<id>.available` | `true` / `false` | 可用性 | 团队资产（02） |
| `skills.digest` | 整包指纹 | 整包版本行 | 团队资产（02） |
| `installed_at` / `owner` | 时间 / `loopx_workflow_skills_cli` | 「安装于 / 由谁装」 | 团队资产（02） |
| `source.revision` vs 控制面版本 | `0.5.0` vs `1.0.2` | **版本漂移警告** | 团队资产（02） |
| `project-skill status` | `blocked` + 原因 | **阻塞徽标 + 原因原文** | 团队资产（02） |
| `codex_skills_root_required` | `true` | 根目录要求提示 | 团队资产（02） |
| `host_readback_required` | `false` | 无需宿主读回（说明） | 团队资产（02） |

### 9.6 健康与能力开关

| 字段 | 取值 | 驱动的 UI | 原型承载 |
|---|---|---|---|
| doctor 分区 | 7 个 | **设置页分区结构** | 设置·Agent（03） |
| doctor 标记 | `✓` / `⚠` / `○` | 三档徽标 | 设置·Agent（03） |
| `latest version status` | `newer version is available` | 版本升级提示 | 设置·Agent（03） |
| `rollout DB stale rows` | `2` | 状态库陈旧提示 | 设置·Agent（03） |
| `mcp → N server (M stdio) · K disabled` | 计数 | MCP 摘要行 | 设置·MCP（04） |
| `feature flags` | `38 enabled · 0 overridden` | 能力开关摘要 | 设置·Agent（03） |
| `features.stage` | `stable` / `under development` / `removed` | **阶段徽标** | 设置·Agent（03） |
| `sandbox.approval policy` | `OnRequest` | 运行级权限（≠审批门） | 设置·Agent（03） |
| `sandbox.filesystem sandbox` / `network sandbox` | `restricted` | 权限档位 | 设置·Agent（03） |
| `state` 段各 DB `integrity` | `ok` | 状态库健康点 | 设置·Agent（03） |

---

## 10. 设计点（按 P0 / P1 / P2）

### P0 — 直接影响当前原型的信息架构

| # | 设计点 | 承载位置 | 依据 |
|---|---|---|---|
| 1 | **运行时选择器改为受约束枚举**（9 值 + 歧义消解），默认 `codex-cli` | 设置·Agent（03） | §2 |
| 2 | **设置·MCP 拆三组**：运行时接入 / MCP 服务 / 插件与市场 | 设置·MCP（04） | §1 |
| 3 | **MCP 卡片加「来源」维**（config 直配 / 插件携带）+ `Status` / `Auth` / 脱敏 `Env` | 设置·MCP（04） | §3 |
| 4 | **市场健康逐条呈现**（原文原因），单条失败不拖垮整页 | 设置·MCP（04） | §4 |
| 5 | **技能卡加：来源三态 + 三类健康**（sha256 / 作用域标记 / 版本对齐） | 团队资产（02） | §5 |
| 6 | **「待宿主操作」卡**（原文命令 + 复制 + 明确不自动执行） | 右栏 / 详情 | §8.2 |
| 7 | **两段式确认**（`preview` 咨询性 → `execute` → **读回校验逐项打勾**） | 右栏 / 详情 | §8.1 |
| 8 | **权限配置（运行级）与审批门（任务级）分家** | 设置·Agent（03） vs 右栏 | §6.2 |
| 9 | **doctor 七分区即设置页分区**，三档徽标 | 设置·Agent（03） | §7 |

### P1 — 补语义深度

| # | 设计点 | 承载位置 | 依据 |
|---|---|---|---|
| 10 | 顶栏同步指示改为「一次性 + 条件复检」，非假实时 | 顶栏 | §8.5 |
| 11 | 能力开关清单（`stage` 徽标：stable / under development / removed） | 设置·Agent（03） | §6.3 |
| 12 | 技能包版本 vs 控制面版本的漂移警告 | 团队资产（02） | §5.2 |
| 13 | 命令门面安装态（15 个 surface，逐宿主面显示是否已装） | 设置·Agent（03） | §6.1 |
| 14 | 状态库健康点（5 个 DB + rollout 体积） | 设置·Agent（03） | §7.2 |

### P2 — 增强可信度

| # | 设计点 | 承载位置 |
|---|---|---|
| 15 | 插件市场来源类型标签（local / git） | 设置·MCP（04） |
| 16 | `machine-config` 四阶段（preview → plan revision → apply → rollback）用于配置变更确认 | 全局 |
| 17 | rollout 体积趋势（209 文件 · 263.53 MB）作为本地存储占用提示 | 设置·Agent（03） |

---

## 11. 命名规范（沿用流程文档）

1. 正文首次出现写「中文名（English）」，其后只用中文名；
2. **命令、字段名、枚举值一律保持原样**（必须可复跑）；UI 展示名可中文化；
3. 本页涉及的中文化对照：

| 英文 / 枚举 | UI 展示名 |
|---|---|
| `codex-cli` | Codex CLI |
| `codex-app` | Codex 桌面应用 |
| `codex-app-ssh` | Codex 桌面应用（SSH） |
| `codex-ide-plugin` | Codex IDE 插件 |
| `agent_type` | 运行时类型 |
| `host_loop` | 宿主循环 |
| `mcp_servers` | MCP 服务 |
| `marketplace` | 插件市场 |
| `plugin` | 插件 |
| `skills` | 技能 |
| `doctor` | 体检 |
| `features` | 能力开关 |
| `sandbox.approval policy` | 运行级审批策略 |
| `preview` / `execute` | 预览 / 执行 |

---

## 附录 A · 本文用到的可复跑命令

```sh
# ── Codex 侧（L2）
codex --version
codex doctor                       # 体检全文（--json / --summary / --all / --no-color）
codex mcp list                     # MCP 两张表
codex mcp get <name>
codex plugin list                  # 插件清单（本机当前报市场 manifest 缺失）
codex plugin marketplace list
codex features list                # 能力开关：name / stage / enabled
codex --help                       # 顶层命令面

# ── LoopX 侧（L1，只取交界）
loopx agent-onboard --list-agent-types
loopx --format json agent-onboard --agent-type codex-cli
loopx slash-commands --help
loopx workflow-skills --help
loopx machine-config --help
loopx project-skill status --skill loopx-project --project .

# ── 配置与清单落点（只读）
cat ~/.codex/config.toml
cat ~/.codex/skills/.loopx-skill-install.json
cat ~/.codex/hooks.json
ls  ~/.codex/skills/ ~/.codex/skills/.system/
```

## 附录 B · 本机实测路径

| 项 | 路径 |
|---|---|
| Codex 可执行 | `~/.local/bin/codex` → `~/.codex/packages/standalone/current/bin/codex` |
| Codex 安装根 | `~/.codex/`（standalone 包在 `~/.codex/packages/standalone/releases/0.146.0-aarch64-apple-darwin`） |
| 主配置 | `~/.codex/config.toml` |
| 鉴权 | `~/.codex/auth.json`（`auth storage mode = File`，`stored auth mode = api_key`） |
| 全局指令 | `~/.codex/AGENTS.md` |
| Hooks | `~/.codex/hooks.json`（事件 `PermissionRequest` / `Stop` / `UserPromptSubmit`；信任哈希存在 `config.toml` 的 `[hooks.state."<路径>:<事件>:<序号>"]`） |
| 技能根 | `~/.codex/skills/`（= `CODEX_HOME/skills`） |
| 技能投递清单 | `~/.codex/skills/.loopx-skill-install.json` |
| 插件缓存 | `~/.codex/plugins/cache/` |
| 状态库 | `~/.codex/state_5.sqlite` · `logs_2.sqlite` · `goals_1.sqlite` · `memories_1.sqlite` · `thread_history_1.sqlite` |
| 会话记录 | `~/.codex/sessions/**/*.jsonl` |
| LoopX 可执行 | `/opt/homebrew/bin/loopx` → `~/.local/share/loopx-venv/bin/loopx` |
| LoopX 技能包源 | `~/.local/share/loopx-venv/lib/python3.13/site-packages/skills/<skill>/` |

## 附录 C · 三组必须切开的概念

| 概念 A | 概念 B | 怎么分 |
|---|---|---|
| **Codex 的 MCP 服务**（`codex mcp list`，实际被宿主拉起的工具进程） | LoopX 的**数据连接器**（`loopx connector list`，带 layer/value/score 的 provider 注册表） | 前者归设置·MCP，后者归控制面内部，UI 上不并列 |
| **MCP 服务** | **插件** | 插件可以**携带** MCP 服务（实测 `codex_app` / `cua_repl` 来自插件）——服务卡要给「来源」维，插件卡要给「含服务数」 |
| **运行级权限配置**（`sandbox.approval policy`，这台机器允许什么） | **任务级审批门**（`coordination.requires_parent_approval`，这个任务要不要人点头） | 前者在设置·Agent；后者在右栏审批门。**同名不同物，不可合并** |

## 附录 D · 与本项目其他文档的关系

| 层 | 文档 |
|---|---|
| 认知层 | `docs/research/competitive-intel-huangruiteng-loopx.md` |
| 建议层 | `docs/decisions/loop-management-optimization.md` |
| 流程层 | `docs/plans/2026-09-16-issue-fix-end-to-end-flow.zh.md` |
| **供给层（本文）** | `docs/plans/2026-09-16-codex-runtime-capability-supply.zh.md` |
| 术语层 | `docs/glossary.md` |
