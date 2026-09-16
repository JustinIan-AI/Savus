# Provider 与模型

LoopDesk 通过统一的配置面支持多个 LLM provider。你可以运行直接单模型模式，或启用 SquillaRouter 进行分层路由。

当需要配置 provider、检查模型支持，或在直接模型模式与 router 模式之间选择时，用本页。

## 查看 Provider

从本地安装列出 provider 元数据：

```sh
loopdesk providers list
loopdesk providers list --json
```

从运行中的 gateway 显示运行时 provider 诊断：

```sh
loopdesk providers status
loopdesk providers status openrouter --json
loopdesk providers status --probe-models
```

`providers list` 不需要运行中的 gateway，`providers status` 需要。

## 配置 Provider

交互式：

```sh
loopdesk providers configure openrouter
```

非交互的 onboarding 式配置：

```sh
export OPENROUTER_API_KEY="sk-..."
loopdesk configure provider --provider openrouter --api-key-env OPENROUTER_API_KEY
```

直接 provider 示例：

```sh
loopdesk configure provider --provider openai --model gpt-5.4-mini --api-key-env OPENAI_API_KEY
loopdesk configure provider --provider anthropic --model claude-sonnet-4-5 --api-key-env ANTHROPIC_API_KEY
loopdesk configure provider --provider gemini --model gemini-2.5-flash --api-key-env GEMINI_API_KEY
loopdesk configure provider --provider ollama --model llama3.1
```

API key 优先使用环境变量引用，避免把密钥直接写入配置文件。

## 经 Onboarding 验证的 Provider

本构建暴露以下 onboarding 支持：

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

provider 注册表可能包含面向高级或自托管设置的额外兼容 provider。用你安装上的 `loopdesk providers list` 查看当前目录。

## 模型检查

列出模型：

```sh
loopdesk models list
```

如果基于 runtime 的模型检查无法连接，请启动 gateway：

```sh
loopdesk gateway run
```

对于不需要 gateway 的 provider 元数据，使用：

```sh
loopdesk providers list
```

## 直接模型 vs Router

直接模型模式：

```sh
loopdesk configure router --router disabled
loopdesk configure provider --provider openai --model gpt-5.4-mini --api-key-env OPENAI_API_KEY
```

Router 模式：

```sh
loopdesk configure router --router recommended
```

| 模式 | 适用场景 |
| --- | --- |
| 直接模型 | 你在测试某个确切模型、复现 provider 行为，或核对 provider 计费。 |
| Router 模式 | 你在做常规的个人 agent 使用，成本与任务复杂度随回合变化。 |

路由细节见 [`features/squilla-router.md`](features/squilla-router.md)。

## Provider 排查

从这些开始：

```sh
loopdesk doctor
loopdesk providers status
loopdesk diagnostics on
```

检查：

- API key 环境变量已在 gateway 进程环境中设置；
- 模型 id 与 provider 匹配；
- 兼容 API 的 base URL 正确；
- 代理设置与你的网络一致；
- 调试某个确切 provider/模型时，router 已禁用；
- 配置变更后已重启 gateway。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
