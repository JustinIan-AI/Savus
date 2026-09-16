# 计划任务

LoopDesk 计划任务让你从 gateway 运行周期性或一次性的 agent 工作。它适用于提醒、周期摘要、状态检查、渠道更新与 webhook 投递的自动化。

计划任务通过 `loopdesk cron` 命令组管理。

## 环境要求

计划作业通过 gateway 运行：

```sh
loopdesk gateway run
```

长期本地使用请启动托管 gateway：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

## 列出作业

```sh
loopdesk cron list
loopdesk cron list --agent main
loopdesk cron list --json
```

## 添加间隔作业

每小时运行一次提示：

```sh
loopdesk cron add \
  --every 1h \
  --text "Summarize important project updates" \
  --name hourly-project-check
```

间隔接受诸如 `30s`、`5m` 与 `1h` 的值。

## 添加 Cron 表达式

在指定时区的工作日 09:00 运行：

```sh
loopdesk cron add \
  --cron "0 9 * * 1-5" \
  --tz "America/Los_Angeles" \
  --text "Prepare a short morning brief" \
  --name weekday-morning-brief
```

不想要默认错峰时，使用 `--exact`。

## 添加一次性作业

```sh
loopdesk cron add \
  --at "2026-06-01T09:00:00+00:00" \
  --text "Remind me to review the launch checklist" \
  --name launch-checklist-reminder
```

## 选择会话目标

默认目标是隔离会话。对大多数计划工作而言，这是最不易出意外的选项。

可用目标：

| 目标 | 适用场景 |
| --- | --- |
| `isolated` | 每次计划运行应独立。 |
| `session` | 你希望投递到由运行时使用面配置的指定会话。 |
| `main` | 你希望为主会话产生一个系统事件。 |

示例：

```sh
loopdesk cron add \
  --every 30m \
  --session-target isolated \
  --text "Check for urgent channel updates" \
  --name urgent-update-check
```

## 投递

禁用投递：

```sh
loopdesk cron add \
  --every 1h \
  --text "Create a private summary" \
  --no-deliver \
  --name private-hourly-summary
```

通过 webhook 投递：

```sh
loopdesk cron add \
  --every 1h \
  --text "Post a compact status summary" \
  --webhook-url https://example.com/hooks/loopdesk \
  --webhook-token-env LOOPDESK_WEBHOOK_TOKEN \
  --name webhook-status-summary
```

优先用 `--webhook-token-env` 或 `--webhook-token-file`，而非内联 token，以免密钥落入 shell 历史。

## 查看与运行作业

```sh
loopdesk cron status <job-id>
loopdesk cron runs <job-id>
loopdesk cron runs <job-id> --limit 50
```

立即运行作业：

```sh
loopdesk cron run <job-id> --yes
```

## 更新或删除作业

```sh
loopdesk cron update <job-id> --enabled
loopdesk cron update <job-id> --disabled
loopdesk cron update <job-id> --every 2h
loopdesk cron remove <job-id> --yes
```

主投递目标无法通过 CLI 原地修补。当主渠道或 webhook 目标需要变更时，请删除并重新添加作业。

## 排查

检查 gateway 与作业状态：

```sh
loopdesk gateway status
loopdesk cron list
loopdesk cron status <job-id>
loopdesk cron runs <job-id>
```

如果作业会向渠道发帖，还要检查：

```sh
loopdesk channels status
```

接下来读：

- [`channels.md`](channels.md)
- [`operations.md`](operations.md)
- [`troubleshooting.md`](troubleshooting.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
