# Crynta Terax 调研报告

> 状态：已完成
> 仓库：`crynta/terax-ai`
> 分支：`main`
> 版本：`0.8.6`
> 许可证：Apache-2.0
> 调研日期：2026-07-30
> 来源：`README.md`、`docs/README.md`、`docs/architecture/*`、`CONTRIBUTING.md`、`ROADMAP.md`、`SECURITY.md`、`package.json`、repo 元数据、公开源码结构签名；未 clone 仓库，未执行商业或后端内部系统验证。

## 1. 一句话结论

Terax 是一个 **7-8 MB 的轻量 terminal-first AI-native dev workspace**，本地 PTY/WebGL/编辑/Git/预览/AI 侧栏都打包进一个 Tauri 2 客户端；它的差异不在“更强模型”，而在 **把 AI writing/editing/agentic tools 做成终端原生 primitive，同时保持 local-first、BYOK、no telemetry、local model**。对 LoopDesk 的参考价值主要在：**terminal-native control surface、file/git/pty/network/secret 五层 security grammar、project memory 的 `TERAX.md` convention、live context bridge、approval/plan mode、meta-orchestration external coding agents**；但它仍偏 “one-app dev environment”，不是 portable cross-tool loop-state protocol。

## 2. 产品定位

- 官方定位：**ADE — agentic development environment**；不是 browser、不是 full IDE、不是 general workspace、不是 team collaboration suite。
- 核心主张：
  - terminal-first：PTY fidelity、xterm.js、WebGL、TUI compatibility 是非卖品。
  - lightweight always：7-8 MB bundle、dependency justified、per-tab memory budget。
  - AI as native primitive：agents/tools/autocomplete/voice/slash commands 是一等公民，不是 sidebar 加上去的。
  - local-first：BYOK 或完全本地模型（LM Studio、MLX、Ollama、OpenAI-compatible），no telemetry，no account，keys in OS keychain。
- 与 LoopDesk 的关键差异：
  - Terax 是 **一个 integrated terminal app**，LoopDesk 想成为 **portable control plane over multiple external agent CLIs**。
  - Terax 本地连续性主要在其 **app/session/TERAX.md** 内部，不是明确的 durable `LOOP-STATE.json` style portable handoff。

## 3. 核心功能

| 功能 | 说明 | LoopDesk 可借鉴点 |
| --- | --- | --- |
| Terminal Native | xterm.js + WebGL、多 tab、split panes、true color、inline search、private tab、WSL bridge | terminal-first runtime surface 与 per-tab isolation |
| PTY/Shell | `portable-pty`、zsh/bash/pwsh/fish/cmd、shell init、OSC 7/133、ConPTY、WSL、Job Object | PTY/agent wiring、shell session lifecycle |
| Editor | CodeMirror 6、vim mode、10 editor themes、AI autocomplete、hunk-level diff/reject | editor as runtime primitive 与 diff UX |
| Source Control | stage/unstage/commit/push、branch display、git graph、commit search/filter | lightweight built-in Git UX |
| File Explorer | icon theme、fuzzy search、keyboard navigation、inline rename、attach to AI | file-to-AI attachment primitive |
| Web Preview | auto local dev server detection、image/PDF、sandboxed iframe | scoped local preview surface |
| AI Providers | OpenAI、Anthropic、Google、xAI、Cerebras、Groq、DeepSeek、Mistral、OpenRouter、OpenAI-compatible、LM Studio、MLX、Ollama | provider abstraction + local model first-class |
| Agentic Loop | `streamText` + tools + `stopWhen` step limit、compact、sub-agents、plan mode | agentic run contract + context compaction boundary |
| Sub-Agents | explore/code-review/security/general、whitelist tools、no recursion | read-only reviewer/debugger sub-agent pattern |
| Project Memory | `TERAX.md` at workspace root、auto/generated init prompt、`/init` slash、livecontext bridge | project memory convention + live context bridge |
| Composer/AI First | docked input、attachments、selection chips from terminal/editor、voice、slash commands | multi-surface AI attachment primitive |
| Approval/Plan Mode | mutating tools need approval；plan mode queues edits for batch review | maker/checker/governance primitive |
| Edit Diffs | AI diff tab、per-hunk accept/reject；approval decoupled from write | diff-as-approval-surface pattern |
| Skills/Slash Commands | `/init`、`/plan`、`/claude-code`、TERAX command marker | slash activation + orchestration markers |
| Live Context Bridge | cwd、terminal context、editor selection、optional active file sent into AI turns | live context bridge 是 LoopDesk memory contract 的强参考 |
| Security | IPC/f secret-path deny-list、workspace auth、SSRF guard、AI tool approval、OS keychain、no Node-in-renderer | five-boundary security grammar 与人类 approval primitive |
| Auto-Update | GitHub Releases、Windows signing（SignPath）、AUR/Nix/AppImage/deb/rpm/NSIS | cross-platform release hygiene |

## 4. 技术架构

- Runtime：Tauri 2 + React 19 + TypeScript + Vite + Zustand + Tailwind v4 + shadcn/ui。
- Terminal：xterm.js + WebGL renderer pool + DormantRing + slot pooling；never serialize mid-command。
- Agent：Vercel AI SDK v6；`runAgentStream` resolves model、builds system prompt、prunes reasonings、compacts long context、streams tools、stops by step count。
- Tools：read-only tools auto after deny-list；mutating tools require approval; edit/multi_edit enforce read-before-edit invariant; plan mode batches edits.
- Context：`TERAX.md` live cache；`createContextAwareTransport` injects env + terminal context + optional active file; `compactModelMessages*` does superseded-read elision + tail compaction.
- Storage：sessions/agents/themes in `tauri-plugin-store`; secrets in OS keychain via `keyring`.
- Packaging：AUR、Nix、AppImage、deb、rpm、Windows NSIS、auto-updater。

## 5. 最有价值的 3 个结构细节

1. **Five-boundary security grammar**：IPC、Filesystem、Network、Secret-storage、Terminal-escape-sequence 分别设防；AI HTTP proxy 有 SSRF/DNS-rebinding 防御；fs 安全有 literal path + canonical path 双重检查；secret/credential patterns/protected dirs/write-deny prefixes 都有明确 normalization。
2. **Live context bridge + compact rules**：不是只传 user prompt，而是持续注入 cwd、terminal context、editor selection、optional active file、TERAX.md project memory；compact 不只截断，还先清理已 superseded reads。
3. **Meta-orchestration external coding agents**：slash `/claude-code` 直接把 Claude Code 当成可编排外部 runtime；hook installer manages Claude Code / Codex / Gemini CLI terminal hooks；未来 roadmap 明确写 **Terax agent spawning and managing external coding agents like Claude Code / OpenCode**。

## 6. 可借鉴清单

- approval-as-boundary，不是事后权限；五层 security grammar 可直接映射 LoopDesk 的 IPC / fs / net / secret / osc boundary。
- project memory 不应只靠 chat history；`TERAX.md` + live context bridge + slash init 是成熟 project-local contract。
- live context bridge 证明“当前工作状态”应持续注入模型上下文；cwd / active file / snapshot / selection 都属于 loop continuity。
- compact 应同时处理 superseded reads + tail compaction，不是简单丢弃历史。
- agent-first surface 最可能是 slash commands + selection-to-agent + voice + plan mode，不是重 IDE。
- external coding agent meta-orchestration 已是 Terax next step；LoopDesk 若只做 portable handoff，应更早建立 durable cross-tool loop state。

## 7. 风险与注意点

- **范围太大**：Terax 同时做终端、编辑器、Git、预览、AI、sub-agent、source control、theme；近距离对标会稀释 LoopDesk 的 control-plane 心智。
- **连续性仍是 app-internal**：当前 repo 没有 durable portable `LOOP-STATE.json` cross-tool handoff 叙事。
- **Bookkeeping 较重**：sessions / agents / themes / lsp / updater / release / changelog 都比 LoopDesk v0.1/v0.2 重很多。
- **个人工作流叙事弱**：Terax 卖 “best AI-native terminal”，LoopDesk 应卖 **portable personal agent continuity layer**。

## 8. 建议结论

- 若 LoopDesk 的目标是 **Personal Agent Control Plane**，Terax 应被当作 **terminal-native primitive reference**，不是产品对标：
  - 学习它的 security grammar、live context bridge、compact invariant、plan/approval UX。
  - 学习它把 Claude Code / Codex / Gemini 当作 external runtimes 的接线方式。
  - 但避免复制其 all-in-one app shell、local-only session continuity、体重级 release、重 client surface。
- 推荐 LoopDesk 优先保留：
  - portable `LOOP-STATE.json`
  - cross-tool adapter-first continuity
  - lightweight CLI + local Web UI
  - worktree isolation + makers/checker split + run log

## 9. 证据说明

| 证据项 | 验证方式 | 可信度 |
| --- | --- | --- |
| 功能列表、provider、platform、bundle、security、storage、roadmap | `README.md` + `docs/` + `ROADMAP.md` + `SECURITY.md` + `package.json` | 高 |
| term/pty/editor/git/history/workspace/modules | repo tree + docs architecture list + `CONTRIBUTING.md` layout | 高 |
| security deny-list / canonicalization / approval flow | `docs/architecture/security-model.md` + `src/modules/ai/lib/security.ts` 文本签名 | 高 |
| live context bridge + compact + sub-agents | `docs/architecture/ai-subsystem.md` + `src/modules/ai/lib/useAiLiveBridge.ts` + `compact.ts` 签名 | 高 |
| external hook installer / Claude Code / Codex / Gemini | `src-tauri/src/modules/agent.rs` 文本签名 | 高 |
| frontier skills / local LLM default URLs | `src/modules/ai/lib/slashCommands.ts` + `src/modules/ai/lib/config.ts` 签名 | 高 |
| backend commerce / vendor pricing / private server | 未见公开证据，当前 repo 未提供 | 未验证 |
