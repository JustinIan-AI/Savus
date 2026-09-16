# 配置

LoopDesk 可通过 onboarding 向导、Web UI 配置流程、CLI 命令、环境变量与 TOML 文件进行配置。日常配置用 CLI 命令；只有高级或脚本化部署才直接编辑 TOML。

## 配置加载顺序

LoopDesk 按以下顺序读取配置：

1. `LOOPDESK_GATEWAY_CONFIG_PATH`
2. `./loopdesk.toml`
3. `~/.loopdesk/config.toml`
4. 内置默认值

想写入或检查项目本地配置文件时，用 `--config ./loopdesk.toml`。

## 密钥处理

密钥优先使用环境变量引用：

```sh
export OPENROUTER_API_KEY="sk-..."
loopdesk configure provider --provider openrouter --api-key-env OPENROUTER_API_KEY
```

不要把明文 API key 提交到 TOML 文件、shell 历史、示例或问题报告中。

## 首次运行向导

```sh
loopdesk onboard
```

常用选项：

```sh
loopdesk onboard --if-needed
loopdesk onboard --minimal
loopdesk onboard --provider openrouter --api-key-env OPENROUTER_API_KEY
loopdesk onboard --provider openai --model gpt-5.4-mini --api-key-env OPENAI_API_KEY
loopdesk onboard --provider ollama --model llama3.1
loopdesk onboard status
```

router 模式默认为 `recommended`。想要直接单模型路由时用 `--router disabled`。

## 重新配置单个分节

`configure` 命令编辑选定的分节：

```sh
loopdesk configure provider --provider openrouter --api-key-env OPENROUTER_API_KEY
loopdesk configure router --router recommended
loopdesk configure router --router openrouter-mix
loopdesk configure router --router disabled
loopdesk configure search --search-provider brave --api-key-env BRAVE_SEARCH_API_KEY
loopdesk configure channels
loopdesk configure image-generation
loopdesk configure memory-embedding
```

支持的分节：

- `provider`
- `router`
- `channels`
- `search`
- `image-generation`
- `memory-embedding`

## 配置决策表

| 需求 | 首选命令 |
| --- | --- |
| 首次配置 | `loopdesk onboard` |
| CI 或安装脚本 | `loopdesk onboard --if-needed` |
| 更换 provider | `loopdesk configure provider ...` |
| 启用或禁用路由 | `loopdesk configure router ...` |
| 配置网络搜索 | `loopdesk configure search ...` |
| 配置消息平台 | `loopdesk configure channels` |
| 查看当前值 | `loopdesk config get` |
| 持久化高级键 | `loopdesk config set <key> <value> --config <path>` |

## Provider 配置

查看 provider 支持情况：

```sh
loopdesk providers list
loopdesk providers configure openrouter
loopdesk providers status
```

经过 onboarding 验证的 provider 包括：

- OpenRouter
- OpenAI
- Anthropic
- Ollama
- DeepSeek
- Gemini
- DashScope / Qwen
- Moonshot AI
- Zhipu / Z.AI
- Baidu Qianfan
- Volcengine Ark

LoopDesk 还保留了额外的 OpenAI 兼容或自托管后端的 provider 注册项。用你安装上的 `loopdesk providers list` 查看当前目录。

阅读：[`providers-and-models.md`](providers-and-models.md)

## Router 配置

Router 模式：

| 模式 | 适用场景 |
| --- | --- |
| `recommended` | 想使用所选 provider 的默认路由配置。 |
| `openrouter-mix` | 想使用 OpenRouter 混合模型默认值。 |
| `disabled` | 想让每个回合都用一个已配置的 provider/模型。 |

命令：

```sh
loopdesk configure router --router recommended
loopdesk configure router --router openrouter-mix
loopdesk configure router --router disabled
```

Router 支持的 provider 配置取决于已安装的构建与已配置的 provider。用直接模型运行做评估前，请先阅读 [`features/squilla-router.md`](features/squilla-router.md)。

## 搜索配置

查看搜索 provider：

```sh
loopdesk search list
loopdesk search status
loopdesk search query "LoopDesk release notes"
```

配置搜索：

```sh
loopdesk configure search --search-provider duckduckgo
loopdesk configure search --search-provider brave --api-key-env BRAVE_SEARCH_API_KEY
```

本构建中 runtime 支持的搜索 provider 包括 Brave Search 与 DuckDuckGo。可能存在面向未来或尚未获得 runtime 支持的额外 provider 元数据。

阅读：[`search.md`](search.md)

## Channel 配置

列出支持的渠道类型：

```sh
loopdesk channels types --json
loopdesk channels describe feishu
loopdesk channels add telegram --name personal
loopdesk channels status
```

Channel 保存会更新配置。编辑后重启 gateway：

```sh
loopdesk gateway restart
loopdesk channels status <name> --json
```

细节见 [`channels.md`](channels.md)。

## Memory 配置

常用命令：

```sh
loopdesk memory status
loopdesk memory index
loopdesk memory list
loopdesk memory search "project preference"
loopdesk memory show <path>
loopdesk memory dream
loopdesk memory flush-session <session-key>
```

配置 embedding 行为：

```sh
loopdesk configure memory-embedding
```

Memory 可组合 Markdown 支持的来源与 SQLite 关键词/语义索引。具体的 memory 形态取决于已配置的 provider 与本地 embedding 支持。

阅读：[`features/memory.md`](features/memory.md)

## 沙箱与权限

查看或更改姿态：

```sh
loopdesk sandbox status
loopdesk sandbox on
loopdesk sandbox full
loopdesk sandbox bypass
loopdesk sandbox reset
```

一次性自动化权限：

```sh
loopdesk agent --permissions restricted -m "Read the repo and summarize it"
loopdesk agent --permissions full -m "Make a local patch and run tests"
```

对于必须留在工作区内的无人值守自动化：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-lockdown \
  --scratch-dir /path/to/project/.scratch \
  -m "Investigate and propose the smallest fix"
```

阅读：[`tools-and-sandbox.md`](tools-and-sandbox.md)

## Gateway 绑定

前台：

```sh
loopdesk gateway run --listen 127.0.0.1 --port 18791
```

托管：

```sh
loopdesk gateway start --json
loopdesk gateway status
loopdesk gateway stop
loopdesk gateway restart
```

绑定优先级：

1. `--listen`
2. `--bind`
3. `LOOPDESK_LISTEN`
4. `LOOPDESK_GATEWAY_HOST`
5. config host
6. `127.0.0.1`

## 原始配置编辑

对于高级设置，请查看 `loopdesk.toml.example` 并直接编辑当前生效的配置文件。日常的 provider、router、search、channel 与 sandbox 变更请用 CLI 命令，因为它们可避免常见的键结构错误。

手动改文件后，重启 gateway 并运行：

```sh
loopdesk doctor
loopdesk gateway status
```

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
