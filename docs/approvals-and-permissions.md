# 审批与权限

审批与权限控制 LoopDesk 工具如何被允许行动。当 agent 能写文件、运行 shell 命令、发布交付物、向渠道发帖或调用外部服务时，它们最重要。

在运行无人值守自动化，或给渠道连接的 agent 广泛工具访问权限之前，请先读本页。

## 权限配置

一次性自动化接受显式的权限配置：

```sh
loopdesk agent --permissions restricted -m "Inspect this repo"
loopdesk agent --permissions on -m "Run with host execution and approvals"
loopdesk agent --permissions bypass -m "Trusted local automation"
loopdesk agent --permissions full -m "Fully trusted local automation"
```

实际含义：

| 配置 | 适用场景 |
| --- | --- |
| `restricted` / `off` | 任务应保持保守，避免提权执行。 |
| `on` | 允许主机执行，但审批检查仍然重要。 |
| `bypass` | 你足够信任该任务，可自动授予审批，同时保留敏感路径检查。 |
| `full` | 你完全信任该任务与环境。谨慎使用。 |

对于自动化，优先使用能完成任务的最窄配置。

## 工作区约束

为文件与 shell 工作设置工作区：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-strict \
  -m "Summarize this repo"
```

将写入限制在工作区或临时目录内：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-lockdown \
  --scratch-dir /path/to/project/.scratch \
  -m "Investigate and prepare a minimal patch"
```

对于项目外误写不可接受的无人值守运行，使用 `--workspace-lockdown`。

## 交互式审批

交互式对话使用面可暂停敏感工具调用以等待人工决策。终端对话支持：

```text
/approvals
/approvals reset
/permissions status
/permissions on
/permissions off
/permissions bypass
/permissions full
/forget
```

当需要在对话中检查或重置已缓存的审批决策时，使用这些命令。

Web UI 也提供审批使用面，用于在消息滚动区之外查看待处理动作。

## 沙箱姿态

查看沙箱姿态：

```sh
loopdesk sandbox status
loopdesk sandbox status --json
```

设置姿态：

```sh
loopdesk sandbox on
loopdesk sandbox bypass
loopdesk sandbox full
loopdesk sandbox reset
```

更改全局沙箱姿态后重启 gateway：

```sh
loopdesk gateway restart
```

## 推荐默认值

| 情境 | 推荐做法 |
| --- | --- |
| 在仓库中首次运行 | `--workspace` 加 `--workspace-strict` |
| 只读调查 | `--permissions restricted` |
| 带测试的本地补丁 | `--workspace-lockdown` 加临时目录 |
| 有写入的 Web UI 任务 | 保持审批可见并审查敏感动作 |
| 渠道连接的 agent | 保守权限 + 显式渠道配置 |
| 无人值守自动化 | 限制 timeout/迭代次数，并选择最窄可用权限 |

## 排查

如果某个工具被拒绝：

```sh
loopdesk sandbox status
loopdesk doctor
```

然后检查：

- 该使用面是否支持实时审批；
- 工作区路径是否正确；
- 是否需要重置缓存的审批；
- 该任务是否应以不同的权限配置运行。

接下来读：

- [`tools-and-sandbox.md`](tools-and-sandbox.md)
- [`web-ui.md`](web-ui.md)
- [`channels.md`](channels.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
