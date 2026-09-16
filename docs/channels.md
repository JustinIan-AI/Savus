# 渠道（Channels）

渠道让 LoopDesk 从消息平台运行，同时与 CLI、Web UI 共享同一套 agent runtime。当你希望同一个 agent 从 Slack、Telegram、飞书/Lark、Discord、钉钉、WeCom、Matrix、QQ 或其他受支持适配器应答时，使用渠道。

## 支持的渠道类型

检查你本地的安装：

```sh
loopdesk channels types
loopdesk channels types --json
loopdesk channels describe feishu
```

本构建暴露以下渠道族：

| 类型 | 名称 | 传输 | 是否需要公网 URL |
| --- | --- | --- | :---: |
| `dingtalk` | DingTalk | websocket | 否 |
| `discord` | Discord | websocket | 否 |
| `feishu` | Feishu / Lark | 混合 | 取决于模式 |
| `matrix` | Matrix | websocket | 否 |
| `qq` | QQ Bot | websocket | 否 |
| `slack` | Slack | 混合 | 取决于模式 |
| `telegram` | Telegram | 混合 | 取决于模式 |
| `wecom` | WeCom | webhook | 是 |

本地 `channels describe <type>` 的输出是必填字段、密钥、extras 与重启行为的权威来源。

## 配置流程

交互式配置：

```sh
loopdesk configure channels
```

显式添加渠道：

```sh
loopdesk channels add telegram --name personal
```

按需添加 provider 专属字段。Slack 支持两种模式：

```sh
# Slack Socket Mode：出站 websocket，无需公网 URL。
loopdesk channels add slack --name team \
  --field connection_mode=socket \
  --field app_token=xapp-... \
  --token xoxb-...

# Slack Events API webhook：需要公网 Request URL 与 signing secret。
loopdesk channels add slack --name team-webhook \
  --field connection_mode=webhook \
  --field signing_secret=... \
  --token xoxb-...
```

编辑配置后重启 gateway 进程：

```sh
loopdesk gateway restart
```

验证运行时连接：

```sh
loopdesk channels status
loopdesk channels status personal --json
```

保存渠道只证明配置已写入。`channels status` 才能证明运行中的 gateway 已加载并连上它。

## 管理渠道

```sh
loopdesk channels list
loopdesk channels enable <name>
loopdesk channels disable <name>
loopdesk channels edit <name>
loopdesk channels restart <name>
loopdesk channels logout <name>
loopdesk channels remove <name>
```

配置变更后用 `gateway restart`。只有在针对已加载的实时适配器时，才用 `channels restart <name>`。

## Slack 模式

Slack Socket Mode 使用出站 websocket，不需要公网 Request URL。它需要 bot token（`xoxb-...`）以及保存为 `app_token` 的 app-level token（`xapp-...`）。

Slack webhook 模式使用 Events API Request URL。它需要 bot token 加 `signing_secret`，且 gateway 必须能被 Slack 访问。

当适配器应回复入站会话时，把 `slack_channel_id` 留空。只在想要默认兜底渠道时才设置它。当回复应留在 Slack 线程内时，启用 `reply_in_thread`。

## Webhook 渠道

Slack webhook 模式与 WeCom 需要一个公网、provider 可达的 URL。飞书与 Telegram 可能视模式而定需要。

对于公网渠道：

- 将 gateway 绑定到可达接口；
- 置于可信反向代理或隧道之后；
- 配置认证；
- 仔细检查 provider 回调 URL 与密钥。

受控网络的绑定示例：

```sh
loopdesk gateway run --listen 0.0.0.0 --port 18791
```

不要把未认证的 gateway 暴露到公网。

## 附件与交付物

各渠道适配器在附件与交付物投递行为上可能不同。LoopDesk 通过同一 runtime 路径规范化 agent 执行，但平台传输仍决定文件大小限制、消息线程与上传/下载能力。

当渠道无法直接投递大型交付物时，用 Web UI 交付物卡或会话导出作为恢复路径。

## 排查

如果渠道无响应：

1. 检查配置条目：

   ```sh
   loopdesk channels list
   ```

2. 检查运行时状态：

   ```sh
   loopdesk channels status <name> --json
   ```

3. 配置变更后重启 gateway 进程：

   ```sh
   loopdesk gateway restart
   ```

4. 对于 webhook 渠道，确认公网 URL、provider 回调密钥，以及 gateway 认证/网络边界。

## 本地检查

打开本地 LoopDesk workspace 视图，即可在不离开主控制面的情况下检查已配置的适配器。workspace 视图显示传输状态、重启尝试与本地禁用动作；配置变更与 onboarding 请使用引导式配置或 `channels` CLI 命令。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
