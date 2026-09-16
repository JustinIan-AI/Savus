# 会话与历史

会话是可持久化的 LoopDesk 对话。它让你查看过去的工作、恢复对话、导出记录，或停止仍在运行的回合。

在以下情况使用会话：

- 从 CLI 或 Web UI 继续之前的对话；
- 查找某个交付物、成本报告或渠道线程的会话 key；
- 导出记录用于调试或分享；
- 终止长时间运行的回合而不删除会话；
- 不再需要时删除旧会话。

## 环境要求

会话命令使用 gateway RPC 面。运行大多数会话命令前，先启动或连接 gateway：

```sh
loopdesk gateway run
```

或使用托管的后台 gateway：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

## 列出最近会话

```sh
loopdesk sessions list
loopdesk sessions list --limit 20
loopdesk sessions list --status idle
loopdesk sessions list --agent main
loopdesk sessions list --channel telegram
loopdesk sessions list --since 2026-05-01
```

脚本可用 `--json`：

```sh
loopdesk sessions list --json
```

## 查看会话

```sh
loopdesk sessions show <session-key>
loopdesk sessions show <session-key> --json
```

输出包含解析后的会话 key、agent id、状态、模型、更新时间、标题，以及可用时的最新预览。

## 恢复会话

```sh
loopdesk sessions resume <session-key>
```

这会在已有会话上打开终端对话。想保持同一对话状态、而非新建对话时使用它。

## 终止运行中的回合

```sh
loopdesk sessions abort <session-key>
loopdesk sessions abort <session-key> --json
```

若有运行中的回合，abort 会停止它，但不会删除会话。

## 导出记录

导出 Markdown：

```sh
loopdesk sessions export <session-key>
loopdesk sessions export <session-key> --output session.md
```

导出 JSON：

```sh
loopdesk sessions export <session-key> --format json --output session.json
```

导出的记录对问题报告、审计，或把任务搬进文档都很有用。公开分享导出前，请移除密钥、私有本地路径、provider token 与私有渠道标识。

## 删除会话

```sh
loopdesk sessions delete <session-key>
loopdesk sessions delete <session-key> --yes
```

删除会话用于清理。若之后可能需要记录，请先导出。

## Web UI 工作流

Web UI 使用同一套会话系统。在控制台中，用对话会话选择器切换会话、查看状态并继续最近的工作。

打开：

```text
http://127.0.0.1:18791/control/
```

## 排查

如果命令无法连接 gateway：

```sh
loopdesk gateway status
loopdesk doctor
```

如果旧上下文看起来被摘要化，说明会话可能在上下文压力下压缩了较早的历史。这对长会话是正常的。当精确文本很重要时，导出该会话。

接下来读：

- [`features/compaction-and-cache.md`](features/compaction-and-cache.md)
- [`web-ui.md`](web-ui.md)
- [`operations.md`](operations.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
