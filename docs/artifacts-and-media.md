# 交付物与媒体

LoopDesk 可在 agent 工作中创建并投递文件：报告、HTML 文件、PDF、幻灯片、表格、生成图片及其他交付物。当输出过大、偏视觉、结构化或重要到不宜只留在对话文本里时，使用交付物。

## 交付物

交付物是会话期间创建的用户可见文件。在 Web UI 对话中，runtime 发布它们时会显示为交付物卡。在 CLI 运行中，交付物事件可包含文件名、id 与下载 URL。

常见用途：

- 生成报告；
- 创建独立 HTML 原型；
- 生成 CSV/XLSX 工作簿；
- 创建 PDF 简报；
- 产出幻灯片；
- 打包生成输出以供渠道投递。

直接提出需求：

```text
Create a one-page HTML dashboard from this data and publish it as an artifact.
```

```text
Generate a PDF briefing with sources and publish the final file.
```

## 何时用交付物而非对话

交付物适用于：

- 用户应下载或分享的文件；
- 需要版式的表格或报告；
- 生成的应用、仪表盘或原型；
- 在对话中难以呈现的长输出；
- 平台支持文件上传时的渠道投递。

简短回答、决策与下一步用对话文本。

## 文档技能

LoopDesk 内置常见文档格式的技能：

- `docx` 用于 Word 文档；
- `pptx` 用于 PowerPoint 幻灯片；
- `xlsx` 用于 Excel 工作簿；
- `pdf-toolkit` 用于结构化 PDF 工作；
- `html-to-pdf` 用于带样式的 PDF 渲染。

发现它们：

```sh
loopdesk skills search pdf
loopdesk skills view pptx
loopdesk skills view xlsx
```

部分文档功能需要可选的原生/系统依赖。用 `loopdesk skills list` 与 `loopdesk doctor` 检查就绪情况。

## 图片输入与生成

在终端对话中，发送图片用于分析：

```text
/image /path/to/screenshot.png Describe what is wrong with this UI.
```

配置图片生成：

```sh
loopdesk configure image-generation
```

然后在对话中请求图片：

```text
Generate a clean product mockup image for this landing page.
```

图片 provider 支持取决于已配置的 provider 凭据、可选依赖与运行时策略。

## 文本转语音与媒体辅助

媒体工具族包含图片、PDF 与 TTS 辅助。可用性可能取决于 provider 配置、可选依赖与运行时策略。

当请求的输出天然是文件或资产、而非纯文本答案时，使用媒体辅助。

## 渠道投递

各渠道在文件大小限制、线程行为与上传 API 上不同。若渠道无法直接投递交付物，用 Web UI 交付物卡或会话导出作为恢复使用面。

渠道配置见 [`channels.md`](channels.md)。

## 排查

如果交付物未出现：

1. 检查对话或 CLI 输出中的交付物事件。
2. 打开 Web UI 会话并查看交付物卡。
3. 需要 durable 证据时导出会话：

   ```sh
   loopdesk sessions export <session-key>
   ```

4. 若文档或媒体依赖疑似缺失，运行 `loopdesk doctor`。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
