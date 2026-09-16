# CLI 参考

`loopdesk` CLI 是配置、运行、检查与自动化 LoopDesk 的最快方式。

运行：

```sh
loopdesk --help
loopdesk <command> --help
```

## 主要命令

| 命令 | 用途 |
| --- | --- |
| `loopdesk init` | 初始化工作区。 |
| `loopdesk doctor` | 诊断就绪状态并打印恢复步骤。 |
| `loopdesk onboard` | 运行或查看首次配置。 |
| `loopdesk configure` | 重新配置 provider、router、channels、search、image generation 或 memory embedding。 |
| `loopdesk gateway` | 运行并管理 gateway 服务器。 |
| `loopdesk chat` | 启动交互式终端对话。 |
| `loopdesk agent` | 运行单个便于自动化的 agent 回合。 |
| `loopdesk sessions` | 列出、查看、恢复、终止、删除或导出会话。 |
| `loopdesk skills` | 列出、搜索、查看、安装、更新、发布与检查技能。 |
| `loopdesk memory` | 查看与维护 memory。 |
| `loopdesk channels` | 配置与检查消息渠道。 |
| `loopdesk providers` | 配置与检查 LLM provider。 |
| `loopdesk search` | 配置并使用网络搜索。 |
| `loopdesk sandbox` | 查看或更改默认沙箱姿态。 |
| `loopdesk cron` | 管理 LoopDesk 的计划运行。 |
| `loopdesk cost` | 查看用量与预估成本。 |
| `loopdesk diagnostics` | 启用或禁用运行时诊断日志。 |
| `loopdesk replay` | 从决策日志重放已记录的回合。 |
| `loopdesk migrate` | 从外部 agent runtime 导入状态。 |
| `loopdesk models` | 查看可用模型。 |
| `loopdesk agents` | 管理 durable agent。 |
| `loopdesk mcp-server` | 运行 LoopDesk MCP server 桥接。 |
| `loopdesk dist` | 输出可复现的工作区状态清单。 |
| `loopdesk reset` | 重置会话并同步刷新 memory。 |

## 运行面

Web UI 与 gateway：

```sh
loopdesk gateway run
loopdesk gateway start --json
loopdesk gateway status
loopdesk gateway restart
loopdesk gateway stop
```

终端对话：

```sh
loopdesk chat
loopdesk chat --model gpt-5.4-mini
loopdesk chat --session <session-key>
loopdesk chat --standalone --workspace /path/to/project
```

一次性自动化：

```sh
loopdesk agent -m "Review the current directory"
loopdesk agent --json -m "Return a short machine-readable summary"
loopdesk agent --workspace /path/to/project --workspace-strict -m "Inspect this repo"
loopdesk agent --timeout 600 --max-iterations 30 -m "Run a bounded investigation"
```

常用自动化 flag：

| Flag | 用途 |
| --- | --- |
| `--workspace` | 设置工作区根目录。 |
| `--workspace-strict` | 将只读侧文件工具限制在工作区内。 |
| `--workspace-lockdown` | 将写入限制在工作区或临时目录内。 |
| `--scratch-dir` | 把临时脚本/日志/候选补丁放到已知目录。 |
| `--timeout` | 设置 agent 总墙钟超时。 |
| `--max-iterations` | 限定模型/工具循环次数。 |
| `--max-provider-retries` | 限定 provider 瞬时重试次数。 |
| `--length-capped-continuations` | 限定 provider 输出因长度受限后的自动续写次数。 |
| `--thinking` | 覆盖推理级别。 |
| `--permissions` | 选择 restricted、bypass 或 full 权限姿态。 |
| `--transcript-path` | 写入供自动化使用的 JSONL transcript。 |
| `--usage-path` | 写入 usage JSON。 |
| `--session-db-path` | 跨多次调用持久化会话重放。 |

## 配置命令

Provider 与 router：

```sh
loopdesk onboard
loopdesk onboard status
loopdesk configure provider --provider openrouter --api-key-env OPENROUTER_API_KEY
loopdesk configure router --router recommended
loopdesk providers list
loopdesk providers configure openrouter
loopdesk providers status
```

搜索：

```sh
loopdesk search list
loopdesk search configure duckduckgo
loopdesk search query "latest LoopDesk release"
loopdesk configure search --search-provider duckduckgo
```

渠道：

```sh
loopdesk channels types
loopdesk channels describe telegram
loopdesk channels add telegram --name personal
loopdesk channels list
loopdesk channels status
loopdesk channels enable personal
loopdesk channels disable personal
loopdesk channels restart personal
loopdesk channels remove personal
```

原始配置：

```sh
loopdesk config get llm.provider
loopdesk config set gateway.port 18791
```

更多细节：

- [`configuration.md`](configuration.md)
- [`providers-and-models.md`](providers-and-models.md)
- [`search.md`](search.md)
- [`channels.md`](channels.md)

## 技能与 Meta-Skill

```sh
loopdesk skills list
loopdesk skills search pdf
loopdesk skills view pdf-toolkit
loopdesk skills install <skill-name>
loopdesk skills update --all
loopdesk skills uninstall <skill-name>
loopdesk skills inspect meta-skill-creator
loopdesk skills meta proposals list
loopdesk skills meta runs list
loopdesk skills meta runs show <run-id>
loopdesk skills meta runs steps <run-id>
loopdesk skills meta runs replay <run-id> --dry-run
```

想在调用 meta-skill 前查看其编译后的步骤计划时，用 `skills inspect`。

阅读：

- [`features/skills.md`](features/skills.md)
- [`features/meta-skills.md`](features/meta-skills.md)
- [`features/meta-skill-user-guide.md`](features/meta-skill-user-guide.md)
- [`authoring/meta-skills.md`](authoring/meta-skills.md)

## 会话与历史

```sh
loopdesk sessions list
loopdesk sessions show <session-key>
loopdesk sessions resume <session-key>
loopdesk sessions abort <session-key>
loopdesk sessions export <session-key>
loopdesk sessions delete <session-key>
```

阅读：[`sessions.md`](sessions.md)

## Memory

```sh
loopdesk memory status
loopdesk memory index
loopdesk memory list
loopdesk memory search "preference"
loopdesk memory show <path>
loopdesk memory dream
loopdesk memory flush-session <session-key>
loopdesk memory repair list
loopdesk memory raw-fallbacks list
```

阅读：[`features/memory.md`](features/memory.md)

## Durable Agent 与计划任务

```sh
loopdesk agents list
loopdesk agents add research --name Research --workspace /path/to/research
loopdesk agents delete research
loopdesk cron list
loopdesk cron add --every 1h --text "Summarize important updates" --name hourly-summary
loopdesk cron status <job-id>
loopdesk cron runs <job-id>
```

阅读：

- [`agents.md`](agents.md)
- [`scheduling.md`](scheduling.md)

## 成本、诊断与重放

```sh
loopdesk cost
loopdesk diagnostics status
loopdesk diagnostics on
loopdesk diagnostics off
loopdesk replay --session <session-key> --turn <turn-id>
```

当需要弄清某回合为何如此行为时，用 diagnostics 与 replay。

阅读：

- [`usage-and-cost.md`](usage-and-cost.md)
- [`diagnostics-and-replay.md`](diagnostics-and-replay.md)

## MCP Server 桥接

```sh
loopdesk mcp-server run
loopdesk mcp-server run --gateway ws://localhost:18792/ws
```

阅读：[`mcp-server.md`](mcp-server.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
