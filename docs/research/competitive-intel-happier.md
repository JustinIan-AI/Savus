# Competitive Intelligence — Happier (happier-dev/happier)

> Research date: 2026-07-09
> Source: public GitHub repo `happier-dev/happier` (depth-1 clone), project docs, README, AGENTS.md, architecture docs, feature matrices, protocol spec.
> Audience: LoopDesk product/engineering planning for personal-loop workspace targeting independent developers.

## 1. Research Method

- Cloned `https://github.com/happier-dev/happier` and inspected full project structure, all docs under `docs/`, architecture diagrams, feature matrices, protocol spec, encryption spec, deployment docs, AGENTS.md, CONTRIBUTING.md, and monorepo package layout.
- Cross-referenced with LoopDesk product positioning (`docs/product-positioning.md`), PRD (`docs/prd/personal-loop-workspace.md`), and existing competitive research (`docs/research/competitive-intel-tutti-wesight-multica.md`).

## 2. Product Identity

### 2.1 Positioning
- **Tagline**: "Mobile, Web and Desktop client for Claude Code, Codex, OpenCode, Pi, Cursor, …"
- **Core promise**: run AI coding sessions locally on your computer and continue/control them remotely from phone, browser, or desktop app, without losing context.
- **Origin**: fork of `slopus/happy`, split for faster iteration. MIT licensed.

### 2.2 Target User
- Developers using terminal-based AI coding agents who want cross-device session continuity and remote control.
- Not positioned as an IDE competitor; positioned as a **companion bridge layer** between local agents and remote devices.

### 2.3 Differentiation Claim
- End-to-end encrypted, self-hostable, open-source.
- Cross-device: mobile (iOS/Android) + web + desktop + CLI.
- Multi-provider: Claude Code, Codex, OpenCode, Gemini, Pi, Qwen, Kilo, Kimi, Kiro, Copilot, Auggie (full catalog).

## 3. Architecture Overview

### 3.1 System Shape
- **Monorepo** (Yarn v1 workspaces, ~13,700 TypeScript files, ~90,500 lines in first 500 files).
- **apps/**: `cli`, `server`, `ui` (React Native / Expo), `stack` (orchestration), `bootstrap`, `docs`, `website`.
- **packages/**: `protocol`, `agents`, `cli-common`, `connection-supervisor`, `relay-server`, `release-runtime`, `transfers`, `tests`, `audio-stream-native`, `sherpa-native`.
- **skills/**: `happier-diagnose`, `happier-github-ops`, `happier-release-*`, `happier-session-control`, `happier-testing`.

### 3.2 Backend
- Node.js + Fastify HTTP + Socket.IO realtime.
- Postgres (Prisma ORM), Redis (startup ping + future expansion), S3/MinIO (blob storage).
- Prometheus metrics, Kubernetes manifests, Docker multi-target image.
- `HANDY_MASTER_SECRET`-derived KeyTree for server-side service token encryption.

### 3.3 CLI / Daemon
- CLI (`happier` command) wraps provider CLIs: `happier` → Claude, `happier codex` → Codex, `happier gemini` → Gemini, etc.
- Long-lived daemon process manages session lifecycle, machine presence, local IPC control server.
- Background session spawning from mobile/web via RPC over Socket.IO.
- Local state in `~/.happier/`: `settings.json`, `access.key`, `daemon.state.json`, logs.
- Binary-safe runtime: ships without requiring system Node/npm.

### 3.4 UI
- React Native + Expo → iOS, Android, and web.
- Tauri desktop app (macOS menubar integration).
- Provider-agnostic rendering via canonical tool normalization (V2 pipeline).
- Theme system with Figma token export, dark/light mode.

### 3.5 Protocol
- JSON over HTTP (`/v1`, `/v2`) + Socket.IO (`/v1/updates`).
- Three connection scopes: `user-scoped`, `session-scoped`, `machine-scoped`.
- Persistent `update` events with per-user monotonic `seq` for sync ordering.
- Ephemeral presence/usage events (`activity`, `machine-activity`, `usage`).
- Optimistic concurrency with `expectedVersion` on all versioned fields.
- RPC mechanism for remote tool execution (bash, file ops, ripgrep, difftastic).

### 3.6 Encryption
- **E2EE by default**: session metadata, agent state, messages, machine metadata, daemon state, artifacts, KV values are all client-encrypted opaque blobs to the server.
- Two encryption variants: legacy NaCl secretbox (XSalsa20-Poly1305) and modern AES-256-GCM with per-session/machine data keys.
- Per-entity `dataEncryptionKey` bundles wrapped with ephemeral tweetnacl.box.
- Server only decrypts service tokens (GitHub OAuth, vendor API keys) with a separate KeyTree.
- Optional plaintext-at-rest mode for sessions (feature-gated).

## 4. Core Capabilities

### 4.1 Multi-Provider Agent Catalog
- Catalog-driven agent registration with `AgentId` contract shared across CLI, app, and server.
- Deep integrations: Claude Code (three runtime surfaces: local TUI, Agent SDK remote, legacy remote shim), Codex (app-server, ACP, MCP), OpenCode (server-native, ACP), Gemini (native runtime).
- Generic ACP (Agent Control Protocol) backend for lighter providers: Pi, Qwen, Kilo, Kimi, Kiro, Copilot, Auggie.
- Provider detection, install, auth probing, capability checking, and feature gating per provider.

### 4.2 Session Management
- Create, resume, fork, attach, wake, takeover, handoff sessions.
- Session forking: branch from any point in conversation history.
- Direct sessions: browse, import, and tail provider-native sessions (Codex `~/.codex/sessions`, Claude JSONL).
- Session metadata and agent state with versioned optimistic updates.
- Usage tracking: per-session token count and cost reporting.

### 4.3 Cross-Device Remote Control
- Phone/browser can spawn, monitor, send messages to, and control local coding sessions.
- Machine registration and heartbeat presence (10-minute timeout).
- Session alive/thinking indicators streamed to all connected devices.
- RPC bridge: execute bash, read/write files, search (ripgrep), diff (difftastic) from remote.

### 4.4 Tool Normalization & Rendering
- CLI-boundary V2 normalization: raw provider tool calls → canonical shapes (`Read`, `Bash`, `Patch`, `TodoWrite`, `Diff`).
- App rendering: one renderer per canonical tool name, multiple detail levels (title/summary/full).
- Trace + fixture-driven regression testing for provider tool format drift.
- Legacy and local-control fallback normalization for older sessions.

### 4.5 Execution Runs
- Background/automated task execution with per-provider backends.
- Permission policy resolution per run.
- Sidechain model for Claude teams/swarms participant routing.

### 4.6 Artifacts & KV Store
- User-owned encrypted artifacts (header + body, versioned).
- Key-value store with optimistic concurrency for user settings and state sync.

### 4.7 Social & Sharing
- User relationships, friend invitations.
- Session sharing with access keys.
- Feed system for social activity.
- Voice sessions (ElevenLabs integration, RevenueCat subscription gating).

### 4.8 Deployment Flexibility
- Self-host runtime with guided setup (`happier relay host install`).
- Docker, Proxmox community scripts.
- Release channels: stable, preview, dev.
- SQLite for self-host by default, Postgres for hosted.

### 4.9 Feature Gating
- Centralized feature catalog in `packages/protocol`.
- Server `/v1/features` endpoint with boolean gates.
- Build-time allow/deny policies via env vars.
- CLI, server, and UI all resolve features through canonical decision engines.

## 5. Competitive Comparison with LoopDesk

### 5.1 Overlap Areas

| Dimension | Happier | LoopDesk (v0.1 plan) |
| --- | --- | --- |
| Multi-tool support | ✅ Deep (Claude, Codex, OpenCode, Gemini, Pi, Qwen, Kilo, Kimi, Kiro, Copilot, Auggie) | ✅ Planned (MCP adapter layer, ACP-second) |
| Local CLI | ✅ `happier` wraps provider CLIs | ✅ `loop` CLI planned |
| Session continuity | ✅ Resume, fork, attach, wake, handoff, direct sessions | ✅ Planned (LOOP-STATE.json, memory, session history) |
| End-to-end encryption | ✅ Strong (NaCl + AES-GCM, per-entity keys) | ◯ Not in v0.1 scope |
| Self-hostable | ✅ Guided setup, Docker, Proxmox | ◯ Local-first, no server |
| Cost tracking | ✅ Per-session usage reporting | ✅ Planned (cost controls) |
| Skills | ✅ Internal skills (`skills/` directory) | ✅ Planned (reusable workflow knowledge) |

### 5.2 Key Differentiation

| Dimension | Happier | LoopDesk |
| --- | --- | --- |
| **Core mental model** | Cross-device companion app / remote bridge | Personal loop workspace / context coherence engine |
| **Primary value** | Continue sessions from any device | Keep loop state coherent; decide what runs next |
| **Architecture** | Client-server with relay (cloud or self-host required) | Local-first, no mandatory server |
| **Loop engineering** | Not present; sessions are user-driven | First-class: triage → maker → checker → escalation → run log → stop condition |
| **Workspace state protocol** | Session metadata + KV store (opaque encrypted blobs) | LOOP-STATE.json (structured, portable, tool-readable) |
| **Scheduler / automation** | Execution runs (background task execution) | Loop Engine with scheduler, stop conditions, maker/checker split |
| **Memory** | KV store for settings sync; no explicit cross-session memory | Durable local memory with cross-session continuity |
| **Worktree isolation** | Not present (sessions share machine context) | Planned (git worktree isolation per task) |
| **UI complexity** | Full React Native cross-platform app (iOS/Android/web/desktop) | Minimal local Web UI + CLI |
| **Social features** | Friend invites, session sharing, feed, voice | Not in scope (personal-first) |
| **Provider depth** | Very deep per-provider integration (3 Claude runtimes, 3 Codex transports) | Adapter layer (MCP/ACP), not provider-native |

### 5.3 What Happier Does Well
1. **Cross-device bridge**: the core "start locally, continue from phone" experience is well-executed and unique in the market.
2. **Provider integration depth**: exhaustive per-provider feature matrices, transport fallbacks, and runtime adapters show genuine production maturity.
3. **E2EE architecture**: thoughtful client-encrypted opaque storage means the relay server never sees plaintext.
4. **Tool normalization pipeline**: V2 canonical shapes with fixture-driven regression testing is a strong engineering pattern.
5. **Multi-platform UI**: single codebase (React Native + Expo) shipping to iOS, Android, web, and Tauri desktop is ambitious and real.
6. **Self-hosting story**: guided install, Docker, Proxmox — low barrier for privacy-conscious users.
7. **Agent catalog system**: deterministic, no-magic, catalog-driven provider registration is clean and extensible.
8. **Execution runs**: background automated execution with permission policies is a practical power-user feature.

### 5.4 What Happier Over-Delivers On (relative to LoopDesk's target user)
1. **Cross-device / mobile experience**: independent devs working solo don't typically need phone control of coding sessions.
2. **Social features**: friend invites, feed, session sharing, voice calls are team/social features outside LoopDesk's personal-first scope.
3. **Cloud relay infrastructure**: Postgres + Redis + S3 + Socket.IO relay is heavy for a personal tool.
4. **Provider-native deep integration**: three Claude runtimes, three Codex transports is integration debt that a thinner adapter layer avoids.

### 5.5 What Happier Under-Delivers On (relative to LoopDesk's target user)
1. **No loop engineering methodology**: sessions are user-driven; no triage, no maker/checker split, no automated stop conditions, no structured run log.
2. **No structured workspace state**: session metadata is encrypted opaque blobs; no portable state file that other tools can read (contrast: `LOOP-STATE.json`).
3. **No cross-session memory**: KV store handles settings sync, but there's no durable memory system that accumulates decisions, skills, and context across sessions.
4. **No worktree isolation**: sessions share the same machine context; no git-worktree-per-task isolation.
5. **No task scheduling / loop engine**: execution runs are fire-and-forget background tasks, not a scheduler with cost guards, priority, and dependency-aware sequencing.
6. **Server dependency**: even self-hosted, Happier requires running a relay server (Postgres, Redis, S3). Not truly local-first.
7. **No tool-agnostic context transfer**: sessions are provider-scoped; starting in Claude and continuing in Codex means creating a new session, not transferring context.

## 6. Threat Assessment

### 6.1 Direct Competitive Threat: Medium
Happier and LoopDesk target the same user (independent developer using multiple AI coding tools) but solve fundamentally different problems:
- Happier: "control your sessions from anywhere" (device mobility).
- LoopDesk: "keep your work coherent across tools" (context continuity).

There is overlap in session management and multi-tool support, but the core value propositions are orthogonal.

### 6.2 Risk: Happier Moves Toward LoopDesk's Territory
- If Happier adds cross-provider context transfer, structured workspace state, or loop engineering features, competition would increase.
- Current trajectory suggests Happier is focused on device mobility, provider depth, and social features — not loop methodology.
- **Mitigant**: LoopDesk's local-first, no-server, structured-state approach is architecturally incompatible with Happier's relay model. Pivoting would require fundamental redesign.

### 6.3 Risk: Happier's Provider Depth Makes LoopDesk's Adapter Layer Look Thin
- Happier has production-tested integrations with 10+ providers including deep runtime, auth, resume, fork, and direct-session support.
- LoopDesk's MCP/ACP adapter approach is thinner by design but may initially underperform on provider-specific edge cases.
- **Mitigant**: LoopDesk's adapter approach trades depth for portability. New providers can be added without bespoke backends. Happier's own docs acknowledge "migration themes" about collapsing multiple runtime paths into unified abstractions.

### 6.4 Opportunity: Complementary Rather Than Competing
- Happier could potentially be one of the tools that LoopDesk orchestrates, treating Happier sessions as another runtime surface.
- LoopDesk's `LOOP-STATE.json` could become the context bridge that Happier lacks.

## 7. Takeaways for LoopDesk v0.1

1. **Do not compete on device mobility.** Happier owns the "phone/browser control of coding sessions" space. LoopDesk should stay focused on local-first loop coherence.
2. **Lean into structured workspace state.** `LOOP-STATE.json` is a real differentiator. Happier's opaque encrypted blobs cannot be consumed by other tools. LoopDesk's portable, readable state file enables an ecosystem Happier's architecture can't.
3. **Loop engineering is the core moat.** Triage → maker → checker → escalation → run log → stop condition — Happier has no answer for this. It's LoopDesk's unique selling point.
4. **Cross-session memory matters.** Happier has KV for settings, not for accumulating knowledge. LoopDesk's memory system that carries decisions and skills across sessions is a genuine gap in all competitors.
5. **Keep the adapter layer thin and uniform.** Happier's deep per-provider integration is powerful but creates migration debt (three Claude runtimes, three Codex transports). LoopDesk's uniform MCP/ACP adapter layer is easier to maintain and extend.
6. **No-server is a feature.** Happier requires Postgres + Redis + S3 even self-hosted. LoopDesk's local-first, zero-infrastructure approach eliminates a real barrier for independent developers.
7. **Watch for Happier feature expansion.** If Happier introduces cross-provider context transfer or structured task automation, LoopDesk should already have established its loop engineering story as the reference implementation.
8. **Borrow the good patterns:**
   - V2 tool normalization with fixture-driven regression testing.
   - Catalog-driven agent registration (no magic, deterministic, reviewable).
   - Optimistic concurrency with `expectedVersion` for versioned state.
   - Feature gating with centralized catalog and build-time deny policies.
