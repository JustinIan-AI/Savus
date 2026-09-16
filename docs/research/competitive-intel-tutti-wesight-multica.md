# Competitive Intelligence — Tutti / WeSight / Multica

> ⚠️ 本文的 **Multica** 部分已被更新的专项调研取代（2026-09-15，覆盖 v0.4.43）：见 [`competitive-intel-multica.md`](./competitive-intel-multica.md)（中文）。本文保留为 2026-07-07 的三合一早期记录。

> Research date: 2026-07-07
> Sources: public repo/README signals, local review notes, local repo inspection, and explicit uncertainty markers where external verification was limited.
> Audience: product/engineering planning for a personal-loop workspace targeting independent developers.

## 1. Research Method

- Inspected public repo pages and local review docs for `tutti-os/tutti`, `freestylefly/wesight`, and `multica-ai/multica`.
- Cross-checked local signals: `/Users/freecisco_yan/Documents/trae_projects/agent-harness/wesight-main`, `/Users/freecisco_yan/Documents/trae_projects/HarnessEngineering/multica`, and prior review docs in those trees.
- Marked gaps honestly: Tutti external page fetching was unstable in this environment, so Tutti conclusions rely more on public README signal than on live page verification.

## 2. `tutti-os/tutti`

### 2.1 Product Signal
- Positioning: real-time shared workspace for people and agents to build in tune.
- Key promise: reduce manual context handoff between agents by sharing the same visible workspace.
- Stated fit: independent developers, designers, PMs, content creators using multiple AI agents.

### 2.2 Core Capabilities
- Shared workspace for context, files, apps, and tasks across agents.
- Cross-agent referencing: reference past conversations, files, app invocations, and tasks from one agent surface while working in another.
- App ecosystem: image generation, UI/UX design, docs, presentations usable by both users and agents.
- Task orchestration: multi-agent sequencing/parallelism with visibility into what each agent changed.
- Tutti VM: cloud room concept for shared agent workspaces across people/devices.

### 2.3 Tech/Platform Signal
- Public README emphasizes workspace, real-time collaboration, and agent handoff rather than a single OS/runtime stack.
- Official site: `tutti.sh`
- License: Apache 2.0

### 2.4 Uncertainties
- External fetch verification was limited; repo content is best treated as public-signal README only.
- Exact architecture, data model, offline behavior, and local-vs-cloud split need README/page confirmation.

## 3. `freestylefly/wesight`

### 3.1 Product Signal
- Positioning: local AI Agent desktop workstation that visualizes terminal-native coding agents.
- Key promise: unify multiple coding agents, model routing, permissions, IM access, file changes, and runtime metrics in one GUI.
- Target user: developers who want multiple coding agents without complex terminal setup.

### 3.2 Core Capabilities
- Multi-engine support: Claude Code, Codex, OpenClaw, Hermes Agent, OpenCode, Qwen Code, DeepSeek-TUI, built-in runtime.
- Chat + tool UI: visualize messages, file writes, tool execution, and approvals.
- Runtime dashboard: engine, model, tokens, TTFT, TPS, tool duration, step count, status, total time.
- IM integration: bot-based task access through messaging channels.
- Skill system: SkillHub + built-in skills + scheduled tasks + memory + extensibility.
- Local persistence: SQLite-backed settings, sessions, messages, runtime calls, skills, and login state.
- Session recovery: restore prior sessions after restart.
- Memory: extract preferences and long-term context across sessions.
- Sandbox/execution modes: execution mode and permission confirmation flow.

### 3.3 Architecture Signal
- Desktop-first Electron app.
- Layered architecture: GUI renderer -> Cowork task protocol -> runtime adapters -> OpenClaw/built-in engines.
- Cowork abstraction: GUI consumes Cowork-standard events rather than engine-specific protocols.
- Local daemon/runtime lifecycle: install/start/ready/running/error state and config sync.

### 3.4 Uncertainties
- Public page fetch was unstable; conclusions rely on local repo and existing review docs.
- Cloud sync/multi-user sharing is not a primary README signal; treat as likely local-first unless confirmed otherwise.

## 4. `multica-ai/multica`

### 4.1 Product Signal
- Positioning: turn coding agents into real teammates inside a shared collaboration platform.
- Key promise: workspace-based issue management where humans and agents share boards, conversations, and task state.
- Target user: small teams and power users who want agent-assisted development with task visibility.

### 4.2 Core Capabilities
- Workspace isolation: issue, agent, project, skill, and member isolation per workspace.
- Issue board: backlog, todo, in_progress, in_review, done, blocked, cancelled; list and board views.
- Polymorphic actor: assign issues to members or agents; agents can comment and create issues.
- Agent config: provider, runtime, instructions, env, MCP config, skills, max concurrency.
- Runtime + daemon: local daemon auto-discovers coding CLIs and registers runtimes.
- Session resumption: preserve workdir and conversation history for repeated agent work.
- Skill system: reusable skill content + files mounted into agent runs.
- Autopilot: cron/webhook/manual triggers; create_issue or run_only modes; skip/queue/replace concurrency.
- Inbox + notifications: issue assignment, @ mentions, subscriptions for creators/assignees/agents.
- Realtime: WebSocket events for issues, tasks, inbox, and chat.

### 4.3 Architecture Signal
- Monorepo: Next.js web + Electron desktop + Go backend + daemon.
- Data layer: PostgreSQL 17 + pgvector, 28 core tables, sqlc-generated code.
- Realtime: WebSocket hub and room-based event broadcasting.
- Local execution: daemon launches and monitors local coding agent CLIs.

### 4.4 Uncertainties
- Local repo inspection is available, but public repo fetch/review still recommended to confirm README claims.
- Strong team/collaboration focus; solo personal-loop fit is weaker by design.

## 5. Feature Comparison Matrix

| Dimension | Tutti | WeSight | Multica |
| --- | --- | --- | --- |
| Primary metaphor | shared agent workspace | desktop agent workstation | agent teammate task board |
| Target user | multi-agent creators/developers | developers who want GUI for coding agents | small teams using agents as teammates |
| Local-first | unclear / likely hybrid | strong local-first signal | local execution, cloud/web+desktop sync |
| Multi-agent | core | strong | strong |
| Cross-tool context | core | strong via unified runtime layer | strong via issue + session resumption |
| App ecosystem | design/docs/presentation tools | skills, IM, scheduled tasks, desktop extensions | skills, autopilot, notifications |
| Task orchestration | visible handoff + orchestration | session/runtime orchestration | issue board + autopilot scheduling |
| Session continuity | cross-agent reference | local session restore + memory | session resumption + workdir preservation |
| IM/bridge | not primary | first-class | not primary |
| Team sharing | Tutti VM room concept | weak/not primary | first-class workspace/member model |
| Observability | workspace activity | runtime metrics dashboard | issue/task realtime events |
| Execution model | agent runs in shared workspace | local runtime adapters + sandbox modes | local daemon + coding agent CLIs |
| Tech stack | workspace/app layer | Electron + Cowork + OpenClaw adapters | Next.js + Electron + Go + Postgres |

## 6. Competitive Analysis

### 6.1 Direct relevance to personal-loop workspace
- Tutti is the closest mental competitor because it targets exactly the pain point of repeated context copying between agents.
- WeSight is a strong adjacent competitor because it unifies multiple coding agents and makes runtime state visible.
- Multica is less of a direct competitor for independent developers; it is more useful as an architecture/reference competitor for runtime/skill/autopilot patterns.

### 6.2 Strategic differentiation
- If the goal is a lightweight personal-loop workspace for one developer across Claude Code, Codex, Codebuddy, Trae, Gemini, and similar tooling:
  - Tutti wins on agent handoff UX.
  - WeSight wins on local desktop/runtime visibility.
  - Multica wins on structured task management.
- The opportunity is likely a hybrid that none currently owns cleanly:
  - Tutti-like shared context flow
  - WeSight-like local runtime visibility
  - Multica-like loop/skill/state persistence
  - plus loop engineering: L1->L2->L3 readiness, cost guardrails, maker/checker split.

### 6.3 Gaps vs our direction
- Tutti: may be too collaboration/cloud-room oriented for solo personal loop.
- WeSight: may be too GUI/desktop/engine-integration oriented, which risks becoming another runtime wrapper instead of a context-layer product.
- Multica: too team/workspace/permission oriented for personal-loop minimalism.

## 7. Recommendations

- Treat Tutti as the primary competitive signal for cross-agent context handoff.
- Treat WeSight as the primary competitive signal for local runtime visibility and multi-engine unification.
- Treat Multica as the primary reference for runtime/skill/session patterns, not as the product model to copy for solo users.
- Recommended focus for differentiation:
  - local-first personal loop state
  - cross-tool adapter strategy with MCP + ACP
  - loop engineering guardrails
  - minimal but powerful workspace state protocol

## 8. Open Questions
- Confirm Tutti public README and live site for exact feature set and offline/local behavior.
- Confirm whether Tutti/VM is priced for individuals or primarily teams.
- Confirm WeSight roadmap for multi-user vs personal-only.
- Confirm Multica personal-mode suitability or whether it is explicitly team-only.
