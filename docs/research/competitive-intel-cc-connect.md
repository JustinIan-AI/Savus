# Competitive Intelligence — cc-connect (chenhg5/cc-connect)

> Research date: 2026-07-13
> Source: public GitHub repo `chenhg5/cc-connect` README and public repo metadata; deeper doc extraction was limited by environment/network restrictions during research.
> Audience: LoopDesk product/engineering planning for personal-loop workspace targeting independent developers.

## 1. Research Method

- Inspected public repo metadata and README for `chenhg5/cc-connect` on GitHub.
- Cross-referenced with LoopDesk product positioning (`docs/product-positioning.md`), PRD (`docs/prd/personal-loop-workspace.md`), architecture (`docs/architecture/personal-loop-workspace.md`), and prior competitive research (`docs/research/competitive-intel-happier.md`, `docs/research/competitive-intel-zleap-agent.md`).
- Did not perform a full local docs sweep because some doc-fetch paths were unavailable in this environment; the report focuses on verified README/public-repo signals.

## 2. Product Identity

### 2.1 Positioning
- **Tagline**: bridge local AI coding agents to messaging platforms.
- **Core promise**: chat with a local AI dev assistant from Feishu/Lark, DingTalk, Slack, Telegram, Discord, LINE, WeChat Work, and other IM clients; no public IP required for most platforms.
- **Origin**: independent open-source project by `chenhg5`; MIT license inferred from README badge; Go implementation.

### 2.2 Target User
- Developers who already use local AI coding CLIs and want to continue or supervise those sessions from chat apps.
- Not primarily a meta-orchestrator for multi-tool continuity; it is a **chat bridge / remote control layer** for local agent CLIs.

### 2.3 Differentiation Claim
- 10+ supported local agents, including Claude Code, Codex, Cursor Agent, Gemini CLI, Qoder CLI, OpenCode, iFlow CLI, Kimi CLI, Pi, Copilot, and ACP-compatible agents.
- 13 chat platforms supported, including Feishu, DingTalk, Slack, Telegram, Discord, WeChat Work, Weibo, LINE, QQ, QQ Bot, Matrix, WPS Xiezuo, and personal WeChat via ilink.
- Most platforms use zero-public-IP transports: WebSocket, Socket Mode, long polling, or gateway flows rather than requiring inbound internet exposure.

## 3. Architecture Overview

### 3.1 System Shape
- Implementation language: Go.
- Single-process supervisor model rather than a full IDE or local-first workspace runtime.
- Multi-project support: one process can manage multiple projects, each with its own agent and platform configuration.

### 3.2 Runtime Model
- Runs locally and acts as a bridge between local coding agents and IM platforms.
- Offers a Web UI for configuration, but the service still needs to be run separately from the admin UI.
- Persists local configuration under `~/.cc-connect/`, including `config.toml`.
- Supports provider/model switching, permission modes, session management, work-directory switching, cron tasks, memory instructions, attachment send-back, TTS, and doctor/preflight checks.

### 3.3 Protocol / Transport
- Platform-specific transports rather than one unified gateway protocol:
  - Feishu/Lark: WebSocket.
  - DingTalk: Stream.
  - WPS Xiezuo: WebSocket.
  - Telegram: long polling.
  - Slack: Socket Mode.
  - Discord: gateway.
  - WeChat Work: WebSocket / webhook.
  - Weixin personal: HTTP long polling.
  - QQ / QQ Bot: WebSocket.
  - Matrix: long polling.
- No public evidence that cc-connect defines or owns a cross-tool workspace state protocol comparable to LoopDesk's `LOOP-STATE.json`.

### 3.4 Observability
- v1.3.3 adds blackbox testing, CUJ testing, provider-resume regression suites, and context-usage reporting in reply footers.
- README explicitly mentions timeout hardening for long-running turns.

## 4. Core Capabilities

### 4.1 Agent Coverage
- Supports native first-class integrations for Claude Code, Codex, Cursor, Gemini CLI, Qoder CLI, OpenCode, iFlow CLI, Kimi CLI, Pi, Copilot, Devin, and ACP-compatible agents.
- Provider ecosystem includes presets for NekoCode, VisionCoder, AIHubMix, MiniMax M3, and relay-style providers.
- Recent hardening around Codex `request_user_input`, Claude Code permission hooks, Kimi/OpenCode/Pi resume flows, and agent-driven TTS.

### 4.2 Platform Coverage
- Supports 13 messaging platforms with documented setup paths.
- Rich inbound/outbound coverage for text, slash commands, markdown/cards, images, files, audio/video, streaming replies, group/channel use, and private chat.
- Some capabilities are partial or limited by vendor APIs, especially speech/ASR/TTS and some card formats.

### 4.3 Session / Workflow Control
- Chat-first control surface:
  - `/new`, `/list`, `/switch`, `/current`
  - `/dir` / `/cd` for work-directory history
  - `/model`, `/provider switch`, `/reasoning`, `/mode`
  - `/memory`, `/cron`, `/cancel`, `/timer`, `/ps`
- Project-level auto session reset after idle time to reduce stale context ingestion.
- OS-user isolation via `run_as_user` for Claude Code on Linux/macOS.
- Permission model with `/permit`, admin allowlists, and unauthorized-sender handling.

### 4.4 Multimodal / Attachment Support
- Attachment send-back for screenshots, charts, PDFs, bundles, and generated files.
- Voice/image support via STT/TTS forwarding where platform/provider allows.
- Attachment caps and configurable max attachment size.

### 4.5 Maturity / Release Posture
- Public repo shows active development as of mid-2026.
- v1.3.3 described as the first stable release after multiple betas, with no breaking changes from v1.3.3-beta.
- 478 open issues on public repo metadata, which suggests active user base and ongoing maintenance burden.

## 5. Competitive Assessment vs LoopDesk

### 5.1 Where cc-connect Is Stronger / More Complete
- **Platform breadth**: 13 messaging platforms vs LoopDesk's current loop-workspace and local adapter focus.
- **Agent catalog breadth**: many named CLIs already supported; LoopDesk targets adapters for Claude Code, Codex, Codebuddy, Trae, Gemini, and local CLIs, but not yet at this catalog scale.
- **Chat UX depth**: slash commands, provider switching, cron, cancel, timer, memory edits, attachment send-back, and rich-media flows are already implemented.
- **Operational hardening**: long-running turn caps, resume regression suites, blackbox/CUJ tests, and platform-specific edge-case handling are visible in the README and changelog.
- **Self-hostable local bridge**: no public-IP requirement on many platforms is a real usability win for developers behind NAT/corporate networks.

### 5.2 Where LoopDesk Has Structural Advantages
- **Problem definition**: LoopDesk is a personal loop workspace with durable local state; cc-connect is a local-agent-to-IM bridge. They are adjacent, but not identical.
- **Portable state contract**: LoopDesk's `LOOP-STATE.json` / `loop_workspace` model is explicitly designed to be readable across tools; cc-connect does not advertise an equivalent portable loop state.
- **Local-first artifact + memory surface**: LoopDesk plans durable memory, skills, artifacts, worktrees, cost controls, approvals, and run logs as first-class workspace entities.
- **Worktree isolation**: LoopDesk's v0.1 explicitly targets filesystem isolation; cc-connect offers OS-user isolation for Claude Code, but not a generalized worktree-first loop workspace.
- **Cost/safety control focus**: LoopDesk treats kill switch, denylist, budget cap, approvals, and stop conditions as core product concerns; cc-connect mentions permission modes but does not market itself as a cost/safety control plane.

### 5.3 Overlap / Adjacent Threat
- **Developer attention overlap**: independent developers using Claude Code or Codex could choose either tool; cc-connect wins if the primary pain is “continue coding from chat.”
- **Memory expectation overlap**: cc-connect's `/memory` and chat-driven instruction editing may set user expectations for conversational memory editing.
- **Context-drift awareness**: cc-connect already treats idle session reset and stale context ingestion as a problem, which means LoopDesk cannot rely on that being an unsolved pain point.
- **Not a direct replacement threat**: cc-connect does not position itself as a loop workspace, cross-tool state layer, or worktree isolation system.

## 6. Takeaways for LoopDesk v0.1

1. **Keep LoopDesk narrow and workspace-first.** cc-connect already owns the chat-bridge category; LoopDesk should avoid competing on platform breadth and instead own local loop continuity, durable state, and worktree isolation.

2. **Make `LOOP-STATE.json` a defensible moat.** If LoopDesk can make its state file the portable contract between Claude Code, Codex, Trae, Gemini, and local CLIs, that is a differentiation cc-connect cannot easily copy.

3. **Treat long-running turn safety as table stakes.** cc-connect's `max_turn_time_mins`, soft-stop, force-kill, auto-resume, and `/cancel` imply users expect reliable timeout and interruption behavior.

4. **Invest in memory/skill/artifact UX, not chat platform count.** For LoopDesk's target user, the value is local continuity and reusable workflow knowledge, not adding more IM channels.

5. **Use lightweight local-first as a competitive advantage.** cc-connect adds a supervisor process and platform-specific transport integrations; LoopDesk should preserve its simpler local install story and avoid heavyweight infrastructure unless it buys clear workspace value.

## 7. Evidence / References

- Public repo metadata:
  - `https://github.com/chenhg5/cc-connect`
  - repo metadata: `full_name: chenhg5/cc-connect`, `language: Go`, `archived: false`, `disabled: false`, `default_branch: main`
- README-derived signals:
  - README title and support matrix: `chenhg5/cc-connect: Bridge local AI coding agents ...`
  - installation/config guidance: `npm install -g cc-connect`, `brew install cc-connect`, `cc-connect web`, `~/.cc-connect/config.toml`
  - v1.3.3 changelog highlights and platform capability matrix
- LoopDesk reference docs:
  - `docs/product-positioning.md`
  - `docs/prd/personal-loop-workspace.md`
  - `docs/architecture/personal-loop-workspace.md`
