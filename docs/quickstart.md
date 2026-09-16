# 快速开始

本指南帮助你在本地完成 LoopDesk 的安装、配置与运行。默认你要的是标准产品体验：终端命令、本地 Web UI、SquillaRouter、memory/search 支持，以及安全的本地默认值。

## 环境要求

- 终端安装需要 Python 3.12 或更高版本。
- 推荐使用 `uv` 进行终端安装。
- 仅从源码安装时才需要 Git 与 Git LFS。
- 除非使用 Ollama 等本地 provider，否则需要一个 provider API key。

## 推荐安装

用推荐 extras 安装当前发布 wheel：

```sh
uv tool install --python 3.12 "loopdesk[recommended] @ https://github.com/loopdesk/loopdesk/releases/download/v0.3.1/loopdesk-0.3.1-py3-none-any.whl"
```

`recommended` extra 包含 SquillaRouter 依赖，以及默认产品体验所需的 memory/search 支持。

若安装后找不到 `loopdesk`，请打开新的 shell 或运行：

```sh
uv tool update-shell
```

## 首次运行配置

交互式配置：

```sh
loopdesk onboard
```

脚本友好的配置：

```sh
export OPENROUTER_API_KEY="sk-..."
loopdesk onboard --provider openrouter --api-key-env OPENROUTER_API_KEY
```

常用变体：

```sh
loopdesk onboard --if-needed
loopdesk onboard --minimal
loopdesk onboard --provider openai --api-key-env OPENAI_API_KEY
loopdesk onboard --provider ollama --model llama3.1
```

`--if-needed` 适合安装脚本，因为它不会重写已就绪的配置。`--minimal` 只配置 provider 路径，跳过可选的 channels/search/image-generation 部分。

查看 onboarding 状态：

```sh
loopdesk onboard status
```

## 运行 Gateway

前台 gateway：

```sh
loopdesk gateway run
```

带就绪等待的后台 gateway：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

默认地址：

```text
http://127.0.0.1:18791/control/
```

gateway 默认绑定 loopback 以保证安全。若要绑定到其他地址，需显式开启：

```sh
loopdesk gateway run --listen 0.0.0.0 --port 18791
```

只有配合适当的认证与网络控制时，才应暴露非 loopback 的 gateway。

## 第一次有用运行

打开 Web UI：

```text
http://127.0.0.1:18791/control/
```

启动终端对话：

```sh
loopdesk chat
```

运行一次自动化回合：

```sh
loopdesk agent -m "Inspect this workspace and suggest a test plan"
```

在指定工作区运行一次性任务：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-strict \
  -m "Review the current diff and list the highest-risk changes"
```

需要浏览器对话、审批、配置、渠道、用量与日志时用 Web UI；想要终端对话时用 `loopdesk chat`；需要一次性自动化时用 `loopdesk agent`。

## 恢复工作

恢复终端对话会话：

```sh
loopdesk chat --session <session-key>
```

查看会话：

```sh
loopdesk sessions list
loopdesk sessions show <session-key>
loopdesk sessions export <session-key>
```

当精确历史对调试或交接很重要时，导出会话。

## 检查就绪状态

配置完成后运行：

```sh
loopdesk doctor
loopdesk providers list
loopdesk search list
loopdesk channels types --json
```

gateway 运行时，查看运行状态：

```sh
loopdesk gateway status
loopdesk providers status
loopdesk channels status
loopdesk memory status
```

provider/模型选择细节见 [`providers-and-models.md`](providers-and-models.md)。搜索配置见 [`search.md`](search.md)。

gateway 生命周期、host/port 与暴露指引见 [`gateway.md`](gateway.md)。

## 停止或重启

前台 gateway：

```text
Ctrl+C
```

托管的后台 gateway：

```sh
loopdesk gateway stop
loopdesk gateway restart
```

## 下一步

首次运行之后：

1. 想要网络调研就配置搜索：[`search.md`](search.md)。
2. 想用 Slack、Telegram、飞书/Lark 等其他消息面就启用渠道：[`channels.md`](channels.md)。
3. 想要 durable 召回就了解 memory 行为：[`features/memory.md`](features/memory.md)。
4. 无人值守自动化前，先了解工具权限：[`tools-and-sandbox.md`](tools-and-sandbox.md)。
5. 想要成本感知的模型路由就学习 SquillaRouter：[`features/squilla-router.md`](features/squilla-router.md)。
6. 产品术语不熟悉就查术语表：[`glossary.md`](glossary.md)。

## 从源码安装

想要基于 checkout 的安装时使用源码安装：

```sh
git lfs install
git clone https://github.com/loopdesk/loopdesk.git
cd loopdesk
git lfs pull --include="src/loopdesk/squilla_router/models/**"
bash scripts/install_source.sh
```

开发时使用仓库虚拟环境：

```sh
uv sync --extra recommended --extra dev
uv run loopdesk --help
uv run loopdesk gateway run
```

从源码开发时，请在命令前加 `uv run`，以使用你正在编辑的 checkout。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
