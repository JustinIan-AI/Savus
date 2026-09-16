# Gateway

LoopDesk gateway 是 Web UI、渠道、RPC 客户端、会话、审批、诊断与用量视图背后的本地服务器。大多数日常 LoopDesk 使用面在 gateway 运行时体验最佳。

当你想启动、停止、检查、暴露或排查 gateway 时，用本页。

## 前台 Gateway

在当前终端运行 gateway：

```sh
loopdesk gateway run
```

打开控制台：

```text
http://127.0.0.1:18791/control/
```

用 `Ctrl+C` 停止前台 gateway。

## 托管的后台 Gateway

启动托管后台进程并等待就绪：

```sh
loopdesk gateway start --json
```

查看它：

```sh
loopdesk gateway status
loopdesk gateway status --json
```

重启或停止它：

```sh
loopdesk gateway restart
loopdesk gateway stop
```

对于 Web UI、渠道、计划任务，以及需要跨当前终端标签页存活的本地自动化，请使用托管 gateway。

## Host 与 Port

使用其他端口：

```sh
loopdesk gateway run --port 18792
loopdesk gateway status --port 18792
```

绑定到指定 host：

```sh
loopdesk gateway run --listen 127.0.0.1 --port 18791
```

`--listen` 是绑定 host 的别名；两者同时提供时 `--listen` 优先于 `--bind`。

## 默认安全策略

gateway 默认使用 loopback 范围（通常是 `127.0.0.1`），因为本地 gateway 控制着对话、工具、会话、渠道、审批与配置。

公网绑定需显式开启：

```sh
loopdesk gateway run --listen 0.0.0.0 --port 18791
```

在没有 token 认证、且你不了解网络边界的情况下，不要把 gateway 暴露到不受信任的网络。

## 配置文件路径

使用指定配置文件：

```sh
loopdesk gateway run --config /path/to/loopdesk.toml
loopdesk gateway status --config /path/to/loopdesk.toml
```

LoopDesk 也会读取 [`configuration.md`](configuration.md) 中描述的标准配置位置。

## 远程状态检查

直接检查 gateway URL：

```sh
loopdesk gateway status --gateway ws://localhost:18791/ws
```

当客户端或 MCP 桥接配置了显式 gateway URL 时，这很有用。

## 何时重启

在修改以下内容后重启 gateway：

- provider 或 router 配置；
- channel 配置；
- durable agent 条目；
- 全局沙箱姿态；
- search 或 image-generation 配置；
- 已配置 provider 使用的环境变量。

```sh
loopdesk gateway restart
```

## 排查

检查状态与就绪情况：

```sh
loopdesk gateway status
loopdesk doctor
```

如果端口被占用：

```sh
loopdesk gateway run --port 18792
```

如果 Web UI 无法连接，请确认 URL 与 gateway 的绑定 host 和 port 一致。

接下来读：

- [`web-ui.md`](web-ui.md)
- [`configuration.md`](configuration.md)
- [`channels.md`](channels.md)
- [`loop workspace`](../README.product.md) —— workspace-first 控制面
- [`troubleshooting.md`](troubleshooting.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
