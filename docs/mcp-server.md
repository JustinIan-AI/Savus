# MCP Server 桥接

LoopDesk 可作为面向支持 MCP 客户端的 stdio MCP server 桥接运行。当另一个本地 AI 客户端应通过 Model Context Protocol 调用 LoopDesk 会话工作流时，使用它。

MCP 桥接是一个集成使用面。它与 LoopDesk 的 Web UI、CLI、渠道与 gateway 控制台相互独立。

## 环境要求

需要该桥接时，用 MCP extra 安装 LoopDesk：

```sh
uv tool install --python 3.12 "loopdesk[recommended,mcp] @ https://github.com/loopdesk/loopdesk/releases/download/v0.3.1/loopdesk-0.3.1-py3-none-any.whl"
```

启动 LoopDesk gateway：

```sh
loopdesk gateway run
```

或使用托管 gateway：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

## 运行桥接

```sh
loopdesk mcp-server run
```

默认情况下，桥接连接到：

```text
ws://localhost:18791/ws
```

使用其他 gateway：

```sh
loopdesk mcp-server run --gateway ws://localhost:18792/ws
```

该命令运行一个 stdio MCP server。请配置你的支持 MCP 的客户端，把该命令作为服务器进程启动。

## 安全提示

- 除非有意暴露，否则保持 gateway 绑定在 `127.0.0.1`。
- 不要在 MCP 客户端配置示例中放置 provider key 或渠道密钥。
- 把 MCP 客户端当作另一个工具调用使用面。同样的 LoopDesk 权限、工具、会话与 gateway 状态依然重要。

## 排查

如果桥接无法启动：

```sh
loopdesk gateway status
loopdesk doctor
```

如果命令报告 MCP 依赖缺失，请用 `mcp` extra 重新安装。

接下来读：

- [`configuration.md`](configuration.md)
- [`tools-and-sandbox.md`](tools-and-sandbox.md)
- [`operations.md`](operations.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
