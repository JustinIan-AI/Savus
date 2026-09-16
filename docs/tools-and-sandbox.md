# 工具、审批与沙箱

LoopDesk 工具赋予 agent 有用的能力。策略层、审批使用面、工作区约束与沙箱姿态控制这些工具如何被允许行动。

在运行无人值守自动化、文件编辑、shell 命令或渠道连接的 agent 之前，请先读本页。

聚焦的权限指南见 [`approvals-and-permissions.md`](approvals-and-permissions.md)。

## 内置工具领域

| 领域 | 示例 |
| --- | --- |
| 文件系统 | `read_file`、`write_file`、`edit_file`、`list_dir`、`glob_search`、`grep_search`、表格读取。 |
| Shell 与代码 | `exec_command`、`background_process`、`process`、`execute_code`。 |
| Git | `git_status`、`git_diff`、`git_log`、`git_commit`、`apply_patch`。 |
| Web | `web_search`、`web_fetch`、`http_request`。 |
| Memory | `memory_search`、`memory_save`、`memory_get`、`memory_delete`。 |
| 会话 | `sessions_send`、`sessions_spawn`、`sessions_list`、`sessions_history`、`session_status`。 |
| 交付物 | `publish_artifact`。 |
| 媒体 | 图片生成、PDF、TTS 与媒体辅助。 |
| 技能 | `skill_list`、`skill_view`、`skill_create`、`skill_edit`、`install_skill_deps`、`meta_invoke`。 |
| 管理 | cron 与 gateway 管理。 |
| 渠道/平台 | 消息，以及飞书/Lark 文档、聊天、云盘、wiki、媒体与权限辅助。 |

## 权限模式

无人值守运行时使用更严格的模式：

```sh
loopdesk agent --permissions restricted -m "Inspect this repo"
```

只有信任任务与工作区时，才使用更宽的模式：

```sh
loopdesk agent --permissions full --workspace /path/to/project -m "Run tests and fix failures"
```

交互式工作时，Web UI 审批使用面可暂停敏感工具调用以供审查。对于自动化，请在运行开始前选择权限模式与工作区策略。

阅读：[`approvals-and-permissions.md`](approvals-and-permissions.md)

## 审批流程

取决于权限模式、工具策略、渠道使用面与运行时配置，敏感动作可能暂停以等待人工审批。

审批最重要的场景：

- 文件系统写入；
- shell 命令；
- 外部渠道或 webhook 投递；
- 将被发布的生成交付物；
- 影响其他服务的动作。

想在对话滚动区之外做 durable 审查时，用 Web UI 审批页。

## 工作区控制

读侧限制：

```sh
loopdesk agent --workspace /path/to/project --workspace-strict -m "Summarize this repo"
```

写入约束：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-lockdown \
  --scratch-dir /path/to/project/.scratch \
  -m "Investigate and prepare a minimal patch"
```

`--workspace-lockdown` 面向写入必须留在工作区或临时目录内的自动化。

## 沙箱命令

```sh
loopdesk sandbox status
loopdesk sandbox on
loopdesk sandbox full
loopdesk sandbox bypass
loopdesk sandbox reset
```

沙箱行为取决于平台。请把 `sandbox status` 与 `doctor` 作为当前机器的权威来源。

## 推荐模式

| 任务 | 推荐姿态 |
| --- | --- |
| 只读仓库摘要 | `--workspace` 加 `--workspace-strict` |
| 带测试的本地补丁 | `--workspace`、`--workspace-lockdown` 与临时目录 |
| 可能写入的对话 | Web UI，保持审批可见 |
| 渠道连接的 agent | 保守权限 + 显式渠道配置 |
| Provider/调试调查 | 开启诊断，最小工具权限 |

## Web 安全

LoopDesk web 工具使用 provider 配置与护栏。当网络搜索行为异常时，用 provider 诊断：

```sh
loopdesk search status
loopdesk search query "test query"
loopdesk diagnostics on
```

搜索结果与抓取的页面是外部数据。它们应为答案提供信息，而不应覆盖工具策略或用户指令。

## 工具压缩

大型工具结果在展示给模型前可能被压缩。这是正常的，用于保护活跃上下文窗口。见 [`features/tool-compression.md`](features/tool-compression.md)。

## 交付物与媒体

工具调用可发布交付物并生成媒体。面向用户的交付物、文档、图片、PDF 与 TTS 工作流见 [`artifacts-and-media.md`](artifacts-and-media.md)。

## 排查

如果工具无法运行：

1. 检查权限姿态：

   ```sh
   loopdesk sandbox status
   loopdesk doctor
   ```

2. 检查 gateway 或渠道使用面是否需要审批。
3. 确认工作区路径正确。
4. 对重复失败使用诊断：

   ```sh
   loopdesk diagnostics on
   ```

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
