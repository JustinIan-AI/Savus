# Herdr 调研报告

> 状态：已完成
> 仓库：`herdrdev/herdr`
> 仓库主页：https://github.com/herdrdev/herdr
> 分支：`master`
> 版本：`v0.7.5`
> 下载/打包：GitHub Releases，Homebrew，mise，Nix，AUR，Windows beta 安装器
> 许可证：Apache-2.0
> 调研日期：2026-07-31
> 来源：`README.md` + `AGENTS.md` + `Cargo.toml` + published releases + docs tree + docs/next docs slugs + representative docs 正文（`README.md`, `docs/next/website/src/content/docs/*.mdx`） + repo tree 的 `src/`, `src/detect/manifests/`, `src/integration/assets/`, `docs/next/api/herdr-api.schema.json`；未 clone 仓库，未执行本地 build/CI。

## 1. 一句话结论

herdr 是一个 **terminal-native agent multiplexer / AI coding agent runtime**：同一个 Herdr session 里持久跑多个真实 terminal pane，并把 Claude Code、Codex、Gemini、Devin、OpenCode 等 coding CLI 当作一等 agent target 管理；它的核心卖点不是“更强模型”，而是 **让多个 coding agent 都在真实终端里持续运行、可 detach/restore、可远程 drive、可插件扩展**。对 LoopDesk 的参考价值主要在：**persistent pane/session restore、agent-state taxonomy、plugin manifest + socket API、remote attach/handoff、真实 terminal attach、agent-skill onboarding 模式**；但它仍偏 “runtime-inside-one-terminal-mux”，不是 portable cross-tool loop-state/protocol 层。

## 2. 产品定位

- 官方定位：**terminal workspace manager for AI coding agents** / **agent multiplexer that lives in your terminal**。
- 核心主张：
  - real terminals first：不是 reimplementation，而是真实 PTY pane；保留完整终端兼容性。
  - agent-first multiplexer：不止 terminal split，还能自动识别 coding agent 状态。
  - local remote：本地 detach/reattach、SSH remote attach、可把 remote server stream 回本地终端。
  - pluggable：plugin marketplace + `plugin install owner/repo/subdir` + hook / event / pane / startup lifecycle。
  - lightweight runtime：单 Rust binary，无 Electron app shell。
- 与 LoopDesk 的关键差异：
  - Herdr 是 **your agents live inside Herdr**；LoopDesk 想成为 **portable control layer over external coding agents**。
  - Herdr 的状态连续性很强，但更多是 **inside its own session/sidebar/pane runtime**；当前未见 durable portable `LOOP-STATE.json` cross-tool narrative。

## 3. 核心功能

| 功能 | 说明 | LoopDesk 可借鉴点 |
| --- | --- | --- |
| Workspace / Tab / Pane | workspace 是项目容器；tab 是布局；pane 是真实终端；支持 split、rename、focus、swap、resize、send-input | terminal runtime primitive + layout isolation |
| Mouse-first TUI | click、drag split、right-click menu、双击复制、hyperlink 支持；keyboard plugin 是可选项 | UX 不必强制 kbd-only；鼠标优先适合复杂监控 |
| Agent Detection | 从 foreground / screen manifest / integration 报告识别 agent；公开检测规则按 agent 维护在 `src/detect/manifests/*.toml` | screen-manifest state inference 是成熟方案 |
| Agent State Rollup | `blocked / working / done / idle / unknown`；sidebar 向上 roll up：blocked 影响 pane/tab/workspace | controller-facing state taxonomy |
| Native Agent Resume | 按 agent 记录原生 session resume：Claude Code、Codex、Cursor/Grok/Copilot/Devin/Kimi/OpenCode/Gemini/etc. | cross-tool continuity 的 runtime 形态 |
| Detach/Reattach | `ctrl+b q` detach；agents/processes 继续跑；reattach 恢复 | persistence UX |
| Snapshot Restore | server restart 后恢复 workspace/tab/pane/cwd/layout；shell/process 不保留；可选 screen-history | restart-safe workspace shape |
| Live Handoff | `--handoff` remote/update 时可尝试把 live panes/processes 转给新 server | upgrade-safe live transfer |
| Session namespaces | `herdr session attach work/side-project`；各自有独立 panes/tabs/sockets/state | personal namespace 隔离 |
| Worktree Integration | Git worktree 可在侧栏创建/打开/分组；checkout 到 configurable 目录 | worktree isolation + grouping |
| Remote Attach | `herdr --remote` 薄客户端模式；SSH attach；本地 keybinding snapshot；可传 clipboard image | remote control UX |
| Socket/CLI API | newline-delimited JSON local socket；CLI 覆盖 workspace/tab/pane/agent/worktree/plugin/integration/events/waits；schema/j/event subscriptions | automation surface / adapter grammar |
| Plugins | GitHub `owner/repo[/subdir]` 安装；manifest-driven `[[startup]]`、actions、event hooks、pane entrypoints；env 注入 plugin context；event logs | local extensibility model |
| Marketplace | public GitHub topic `herdr-plugin` 自动索引；30 分钟 refresh；不 review | discovery model |
| Config | TOML：keybindings、theme、worktree、remote、sidebar row layout、notification/sound、logs、agent-session restore、IME、session history、 Kitty graphics | configuration contract |

## 4. 技术架构

- Runtime：单 Rust binary；TUI client 与 server-owned runtime 分离；正在往 “server-owned runtime protocol / one client” 迁移。
- State/data：`AppState` vs `PaneState` vs `PaneRuntime`；render 是 pure；no god objects；平台代码隔离在 `src/platform/<os>.rs`。
- Terminal：`portable-pty` fork + `ratatui` + crossterm；支持 Kitty graphics、IME、selection、mouse、navigate mode、popup、title sync。
- Detection：`src/detect/manifests/*.toml`；remote manifest auto-update 可本地 override；`herdr agent explain` 可解释检测结果。
- Session/Persist：`session.snapshot` bootstrap + event-driven local cache；server restart restore 由 `src/persist/*` 承担；plugin registry state persist。
- Networking：remote attach 走 SSH；experimental `--handoff`；自动 SSH control socket + keepalive fallback；无已知 built-in tunnel/relay SaaS。
- Integrations：Claude Code、Codex、OpenCode、Cursor、Devin、Grok/Copilot、Kimi/Qoder/OpenCode/Hermes/Kilo 等都有 hook/plugin；集成安装 via `herdr integration install <agent>`。

## 5. 最有价值的 3 个结构细节

1. **Real terminal multiplexer, not agent shell wrapper**：Herdr 不把 agent 输出重新渲染成一个普通 chat UI，而是保留真实 terminal；让它能兼容复杂 CLI/TUI、长输出、shell tooling、alternate screen。
2. **Agent state inference as platform capability**：不是只监控是否在线，而是有明确 `blocked/working/done/idle/unknown` 语义、可 rename、可 custom label、可 EXPLAIN，sidebar 可 rollup；这非常接近 “runtime control plane” 的基础块。
3. **Plugin + socket API standardized extensibility**：manifest、build、startup hooks、actions、event hooks、popup/split/tab pane、env context、schema 都文档化；外部脚本/agents 可通过 socket 或 CLI 控制 workspace/tab/pane/agent。

## 6. 可借鉴清单

- real-tty preservation matters：如果 LoopDesk 需要监控 coding agent，应保留真实 PTY stream 而不是只存聊天文本。
- blocked-state taxonomy is valuable：`blocked/working/done/idle/unknown` + rollup 是低成本高信息量的 controller view。
- native-agent resume + live handoff 说明 durable session continuity 不只是聊天记忆；process/session identity 同样关键。
- `agent skill` onboarding 是轻量“让 agent 学会你”模式；比手工写 prompt 更可持续。
- plugin/manifest model 可直接借鉴为 LoopDesk 的 skills/hooks 扩展模型。

## 7. 风险与注意点

- **定位仍是 multiplexer，不是 portable loop protocol**：herdr 让多个 agent 持续跑，但 handoff 最强仍在 Herdr 内部 session/runtime。
- **单机 central runtime 依赖**：所有 workspace/session/state 绑定在 running Herdr server；这与 LoopDesk 的 portable `LOOP-STATE.json` 心智不同。
- **远程 attach 仍偏 SSH/personal**：公开文档没有强调 built-in tunnel/relay、multi-user、team room、或商业托管远控服务；`dcolinmorgan/herdr-remote` 是第三方补充。
- **复杂度边界**：plugins、worktree、remote、IME、popup、kitty graphics 已经很多；LoopDesk 不应复制其全 surface。

## 8. 建议结论

- 若 LoopDesk 的目标是 **Personal Agent Control Plane**，herdr 应被当作 **local agent runtime / multiplexer reference**，不是对标产品：
  - 学习它的 terminal-native control、agent-state rollup、session restore/remote attach、plugin API。
  - 但不要复制其 single-runtime-server-first 心智；LoopDesk 应以 portable state/adapter-first 为核心。
- 推荐 LoopDesk 优先保留：
  - portable `LOOP-STATE.json`
  - cross-tool adapter-first continuity
  - lightweight CLI + local Web UI
  - 适度的 blocked/working/done state view

## 9. 证据说明

| 证据项 | 验证方式 | 可信度 |
| --- | --- | --- |
| 定位 / install / agent 列表 / 平台 / releases | `README.md` + repo metadata + GitHub Releases 元数据 | 高 |
| concepts/session/agents/integrations/plugins/socket-api 正文 | docs/next mdx 文件签名 | 高 |
| Rust 架构与 runtime boundary | `AGENTS.md` 架构原则 + `Cargo.toml` + `src/` tree 签名 | 高 |
| agent detection + resume + remote versions | docs `agents.mdx` / `session-state.mdx` / `persistence-remote.mdx` + `src/detect/manifests/*.toml` 签名 | 高 |
| socket/plugin/manifest schema | `docs/next/api/herdr-api.schema.json` tree + `socket-api.mdx` / `plugins.mdx` 签名 | 高 |
| 后端/商业/定价/team SaaS / tunnel 服务 | 当前公开 repo/docs 未见直接证据 | 未验证 |
