# 排查

从这些开始：

```sh
loopdesk doctor
loopdesk doctor --json
loopdesk gateway status
```

gateway 运行时，<http://127.0.0.1:18791/control/> 的 Web UI 健康视图也会报告就绪情况与恢复步骤。

## 找不到 `loopdesk` 命令

`uv tool install` 之后，请打开新终端或运行：

```sh
uv tool update-shell
```

检查可执行文件：

```sh
command -v loopdesk
```

Windows PowerShell：

```powershell
where.exe loopdesk
```

## Gateway 未运行

启动它：

```sh
loopdesk gateway run
```

或使用托管后台进程：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

打开：

```text
http://127.0.0.1:18791/control/
```

聚焦的 gateway 指南见 [`gateway.md`](gateway.md)。

## 端口已被占用

换一个端口：

```sh
loopdesk gateway run --port 18792
```

或停止托管 gateway：

```sh
loopdesk gateway stop
```

## Provider 未配置

运行：

```sh
loopdesk onboard
loopdesk providers list
loopdesk providers configure openrouter
```

使用环境变量密钥：

```sh
export OPENAI_API_KEY="sk-..."
loopdesk configure provider --provider openai --api-key-env OPENAI_API_KEY
```

## Router 依赖问题

如果 SquillaRouter 无法加载，LoopDesk 仍可用直接模型路由运行。禁用 router：

```sh
loopdesk configure router --router disabled
loopdesk gateway restart
```

在 Windows 上，ONNX Runtime 可能需要 Visual C++ Redistributable for Visual Studio 2015-2022 x64。安装后重启 shell 与 gateway。

## 搜索不工作

检查搜索 provider：

```sh
loopdesk search list
loopdesk search status
```

使用无需 key 的 DuckDuckGo：

```sh
loopdesk configure search --search-provider duckduckgo
```

使用带 key 的 Brave：

```sh
export BRAVE_SEARCH_API_KEY="..."
loopdesk configure search --search-provider brave --api-key-env BRAVE_SEARCH_API_KEY
```

## 渠道配置已保存但渠道离线

编辑渠道配置后重启 gateway：

```sh
loopdesk gateway restart
loopdesk channels status <name> --json
```

对于 webhook 渠道，确认 gateway 对 provider 可达，且回调密钥匹配。

## 某个工具被拒绝

检查沙箱与权限状态：

```sh
loopdesk sandbox status
loopdesk doctor
```

对于一次性运行，选择显式权限姿态：

```sh
loopdesk agent --permissions restricted -m "Read only"
loopdesk agent --permissions full -m "Trusted local automation"
```

## Agent 似乎忘记了旧上下文

长会话可能压缩旧历史。这在上下文压力下是预期行为。

查看会话：

```sh
loopdesk sessions show <session-key>
loopdesk sessions export <session-key>
```

如果精确的旧文本很重要，请把它放进文件、memory 笔记或导出的会话中。

## 某回合太贵或太慢

尝试：

```sh
loopdesk configure router --router recommended
loopdesk diagnostics on
loopdesk cost
```

对于自动化：

```sh
loopdesk agent --max-iterations 20 --timeout 600 -m "Bounded task"
```

大型工具输出见 [`features/tool-compression.md`](features/tool-compression.md)。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
