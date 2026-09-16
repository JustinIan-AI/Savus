# 运维

本指南覆盖日常运维命令：会话、cron、成本、诊断、重放、迁移、durable agent、MCP 与安装清单。请在首次成功对话或 gateway 运行之后使用它。

## 会话

会话是持久的对话/任务历史。用它们恢复、检查、导出或清理此前的 工作。

```sh
loopdesk sessions list
loopdesk sessions show <session-key>
loopdesk sessions resume <session-key>
loopdesk sessions export <session-key>
loopdesk sessions abort <session-key>
loopdesk sessions delete <session-key>
```

当精确的旧上下文很重要，或你想在对话 UI 之外调试长任务时，使用会话导出。

恢复、终止、导出与清理工作流见 [`sessions.md`](sessions.md)。

## Durable Agent

LoopDesk 支持 durable agent 条目，包括内置的 `main` agent。

```sh
loopdesk agents list
loopdesk agents add research --name Research --workspace /path/to/research
loopdesk agents delete research
```

当重复性角色需要独立的工作区、指令或工具配置时，使用 durable agent。agent 配置变更后重启 gateway。

请让每个 durable agent 的指令聚焦该角色，而不是把每个 agent 都变成 `main` 的副本。

agent 示例与概念见 [`agents.md`](agents.md)。

## Cron 与计划运行

Cron 作业按计划运行 LoopDesk 任务。

查看作业：

```sh
loopdesk cron list
loopdesk cron status <job-id>
loopdesk cron runs <job-id>
```

添加一个简单的周期提醒：

```sh
loopdesk cron add \
  --every 1h \
  --text "Check for urgent project updates and summarize them" \
  --name hourly-project-check
```

添加一个每日 cron 式任务：

```sh
loopdesk cron add \
  --cron "0 9 * * 1-5" \
  --tz "America/Los_Angeles" \
  --text "Prepare my weekday morning briefing" \
  --name weekday-briefing
```

管理作业：

```sh
loopdesk cron update <job-id> --enabled
loopdesk cron remove <job-id>
loopdesk cron run <job-id>
```

好的用法：

- 早间简报；
- 周期性调研摘要；
- PR 或 CI 检查；
- 渠道投递的提醒；
- 计划性的 memory 归并或报告任务。

当输出应投递到本地 Web UI 之外的地方时，把 cron 与渠道配合使用。

计划示例、投递选项与排查见 [`scheduling.md`](scheduling.md)。

## 成本与用量

查看用量与预估成本：

```sh
loopdesk cost
loopdesk cost --by-model
loopdesk cost --json
```

在工具密集、路由或长上下文任务之后用成本检查，了解实际的运行时行为。

成本调查工作流见 [`usage-and-cost.md`](usage-and-cost.md)。

## 诊断

诊断有助于解释运行时行为，而不改变核心任务。

```sh
loopdesk diagnostics status
loopdesk diagnostics on
loopdesk diagnostics off
```

在调查以下内容时使用诊断：

- provider 重试行为；
- router 决策；
- 缓存断裂；
- 压缩事件；
- 工具结果压缩；
- 渠道投递失败。

收集到所需证据后关闭诊断。

诊断指引与安全分享说明见 [`diagnostics-and-replay.md`](diagnostics-and-replay.md)。

## 重放

从决策日志重放已记录的回合：

```sh
loopdesk replay --session <session-key> --turn <turn-id>
```

重放适用于复现某个 agent 回合、查看决策元数据，或在原对话已继续之后调试行为。

## 迁移

先预览：

```sh
loopdesk migrate openclaw --json
loopdesk migrate hermes --json
```

查看报告后再应用：

```sh
loopdesk migrate openclaw --apply
loopdesk migrate hermes --apply
```

自定义路径与冲突处理见 [`../MIGRATION.md`](../MIGRATION.md)。

## MCP Server

使用 `mcp` extra 安装时，LoopDesk 可运行 MCP server 桥接：

```sh
loopdesk mcp-server run
```

安装：

```sh
uv tool install --python 3.12 "loopdesk[recommended,mcp] @ https://github.com/loopdesk/loopdesk/releases/download/v0.3.1/loopdesk-0.3.1-py3-none-any.whl"
```

当另一个支持 MCP 的客户端需要访问 LoopDesk 管理的工具或运行时使用面时，使用它。

配置细节见 [`mcp-server.md`](mcp-server.md)。

## 安装清单

输出可复现的工作区状态清单：

```sh
loopdesk dist
```

用于支持、发布 QA 或环境对比。

## 模型

查看可用模型：

```sh
loopdesk models list
```

在本构建中，模型检查可能基于 runtime。如果无法连接，请先启动 gateway：

```sh
loopdesk gateway run
```

对于不需要实时 gateway 的 provider 目录检查，使用：

```sh
loopdesk providers list
```

阅读：[`providers-and-models.md`](providers-and-models.md)

## 健康检查清单

对于令人困惑的安装或运行时：

```sh
loopdesk doctor
loopdesk gateway status
loopdesk providers list
loopdesk search list
loopdesk channels types
loopdesk sandbox status
```

只有在基础健康使用面不够时，才开启诊断。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
