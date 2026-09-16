# 核心功能清单

> 基于对 Tutti、WeSight、Multica、Orca 与 Proma 的竞品评审优化而来。
> 原则：按对个人循环的价值分组，而非按 UI 屏幕或厂商外壳分组。

## 1. Workspace 状态协议

开发者与 agent 正在做什么的单一事实源。

- `LOOP-STATE.json`，包含任务、状态、上次结果、时间戳与人工覆盖历史。
- Workspace memory 索引，用于偏好、决策、可复用事实与项目约定。
- Skills 目录，包含可复用的任务指令、命令与引用。
- Artifacts 目录，包含生成的报告、代码、媒体与导出。
- 可移植的上下文导出/导入，用于在工具或机器之间迁移工作。

## 2. 跨工具适配层

连接外部工具，而不强制单一厂商 UI。

- MCP-first 适配器，处理工具、资源、prompt 与工具结果。
- ACP 适配器，面向支持 ACP 的工具，使用会话生命周期与更新流。
- 面向 Claude Code、Codex、Codebuddy、Trae、Gemini 与本地 CLI 的工具专用适配器。
- 入站与出站事件转换：工具专用输出变为 workspace 状态，workspace 状态变为工具可用的输入。

### 桌面运行时 + 次要使用面

- 桌面优先的本地运行时或打包桌面应用，拥有 gateway、workspace 文件、agent 生命周期、worktree 隔离与最丰富的检查能力。
- 本地 Web UI，用于引导式配置、workspace 检查、审批动作、诊断、重放与导出。
- 可选 IM 远程控制使用面，用于选择工作区、查看状态、审批/拒绝，以及继续已批准工作的有界续跑。
- 桌面优先的边界规则：Web 与 IM 可读取或排队轻量动作，但耐久权威仍是本地 workspace 与桌面运行时。

## 3. Loop 引擎

把重复性工作变成有纪律的自动化，而非临时 prompt。

- Scheduler：cron、立即触发、耐久重启与 pause/kill 控制。
- Triage 技能：决定某个循环应行动、提议还是升级。
- Maker/checker 分离：实现者与验证者相互独立。
- `/goal` 式停止条件与显式完成标准。
- Loop run log：已开始、发现的条目、采取的动作、升级与成本。

## 4. 个人 Memory 与会话连续性

记住重要内容，而不把每条旧消息都塞进上下文。

- 持久 memory，支持本地关键词与语义搜索。
- 长任务的会话压缩与缓存连续性。
- 会话恢复、历史、导出、重放与终止控制。
- 会话到 memory 的刷新，让已完成任务成为可复用知识。
- memory/会话状态降级时的修复与回退路径。

## 5. 技能与 Meta-Skill 运行时

打包可复用判断，而非每次运行都重复意图。

- 编写、检查、安装、启用、禁用与更新技能。
- Meta-skill，用于可重复的多步工作流。
- 面向高信任自动化的重放、审计与提议使用面。
- 为可预测的自动触发而调优的技能描述与 prompt。
- 按 workspace 配置 Skills 与 MCP，使不同工作区可使用不同适配器、provider、技能与 denylist。
- 按 workspace 管理 MCP server 生命周期：启用、禁用、重试、恢复、审计，并绑定到 `LOOP-STATE.json`、run log、审批历史与预算上下文。

## 6. 运行时可见性与本地控制

查看并控制循环在开发者机器上做什么。

- 本地 Web UI 与 CLI 使用面：对话、审批、日志、会话、技能、cron 与健康。
- 运行时状态视图：活跃运行、近期工具活动、待审批与错误。
- 权限模式：只读、受限、完全访问。
- Workspace 约束：严格的路径控制与沙箱姿态。

## 7. 成本观察与安全护栏

防止自动化失控，让开发者保持掌控。

- token 与成本跟踪，按会话、agent、技能与循环汇总。
- 预算上限、日限、kill switch 与最大迭代次数。
- 面向敏感工具调用、写入与外部动作的审批队列。
- 面向歧义、重复失败、高风险与 denylist 路径的升级触发。
- 面向坏运行、失败与恢复的诊断与重放。

## 8. Worktree 隔离

安全运行自动化，而不污染主工作区。

- 为高风险或自动化工作提供按循环的 worktree 或临时目录。
- 循环完成后清理，或保留审计快照。
- 隔离规则，避免并行循环相互覆盖。
- 在相关时，git 感知的循环状态绑定到分支、commit 与 diff。

## v0.1 功能优先级

### 必须有
- Workspace 状态协议：`LOOP-STATE.json`、memory 索引、skills 与 artifacts。
- MCP 适配器，至少支持一个本地 coding agent 工作流。
- Loop 引擎：scheduler、triage、maker/checker 分离与 run log。
- 本地 Web UI + CLI：状态检查、会话控制、审批与成本。
- 个人 memory：持久存储、搜索与会话压缩。

### 应该有
- 面向支持 ACP 工具的 ACP 适配器。
- 面向 Claude Code、Codex、Gemini 与本地 CLI 的工具专用适配器。
- 成本观察：token 跟踪、预算上限与升级。
- 面向自动化循环的 Worktree 隔离。

### 可以有
- 循环结果的 IM 与渠道投递。
- v0.2 中面向钉钉、飞书/Lark、Slack 与 WeCom 的可选 IM 远程控制与通知使用面。
- 类似 Tutti VM 的云房间共享。
- 团队工作区与成员管理。
- 市场式技能生态。

### 初期不做
- 以多用户协作为核心循环。
- 与 WeSight 完全对等的桌面应用功能。
- 类似 Multica 的团队治理与企业 onboarding 流程。
