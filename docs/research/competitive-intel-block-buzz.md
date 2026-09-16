# Competitive Intelligence: Block/Buzz

- **Repo**: [github.com/block/buzz](https://github.com/block/buzz)
- **Owner**: Block, Inc. (formerly Square)
- **License**: Apache 2.0
- **Language**: Rust (relay/backend) + TypeScript/React (desktop/web/mobile)
- **Stars**: ~22,000 | **Forks**: ~2,400 | **Open Issues**: ~1,800
- **Created**: 2026-03-06 | **Last Push**: 2026-08-04 (actively maintained)
- **Tagline**: "A hive mind communication platform"

## 1. What Is Buzz

Buzz is a **self-hostable team workspace** where humans and AI agents share the same rooms, the same protocol, the same identity model, and the same audit trail. It is built on the **Nostr protocol** (NIP-01) — every action (message, reaction, workflow step, git event, canvas edit, voice huddle) is a cryptographically signed event identified by a `kind` integer.

Core thesis: **the relay is the workspace**. One community, one URL, one event log, one identity system, one search index. No GitHub + Discord + CI dashboard + release tools stitched together.

## 2. Architecture

### Stack
- **Relay**: Rust monorepo (Axum WebSocket + REST), single source of truth
- **Storage**: Postgres (events + FTS search), Redis (pub/sub, presence, typing), S3/MinIO (Blossom media)
- **Desktop**: Tauri 2 + React
- **Mobile**: Flutter (channels, forum, search, profile, pairing — in active dev)
- **Protocol**: Nostr NIP-01 wire format + custom kind numbers for enterprise features

### Crate Map (29 workspace members)

| Category | Crates |
|----------|--------|
| **Core** | `buzz-core` (zero-I/O types, NIP-01 filters, Schnorr verify), `buzz-relay` (Axum WS + REST) |
| **Services** | `buzz-db` (Postgres), `buzz-auth` (NIP-42/98 Schnorr auth), `buzz-pubsub` (Redis presence/typing), `buzz-search` (Postgres FTS), `buzz-audit` (hash-chain log) |
| **Agent Surface** | `buzz-cli` (agent-first CLI, JSON in/out), `buzz-acp` (ACP harness for Goose/Codex/Claude Code), `buzz-agent` (ACP agent), `buzz-dev-mcp` (shell + file-edit MCP server), `buzz-workflow` (YAML automation), `buzz-persona` (agent persona packs) |
| **Git & Pairing** | `git-sign-nostr`, `git-credential-nostr` (nostr-signed git), `buzz-pair-relay`, `buzz-pairing-cli` |
| **Infra** | `buzz-relay-mesh` (iroh-based inter-relay mesh), `buzz-voice` (WebSocket Opus voice relay), `buzz-backend-kubernetes` (remote agent deploy), `buzz-media` (Blossom/S3) |
| **Shared** | `buzz-sdk` (typed event builders), `buzz-conformance`, `buzz-ws-client`, `buzz-test-client`, `buzz-admin`, `sprig` |

### Key Design Decisions
- **Fan-out**: Three-tier subscription registry — (channel_id, kind) index → channel wildcard → global scan
- **Auth**: NIP-42 (WebSocket Schnorr challenge/response) + NIP-98 (HTTP bridge)
- **Multi-tenancy**: Community = tenant boundary, selected by request host. Isolation proven in TLA+ and Tamarin.
- **Audit**: Hash-chain audit log, tamper-evident
- **Zero unsafe Rust, zero panics, bounded process lifetime/output**

## 3. Surfaces

| Surface | Model |
|---------|-------|
| 🏠 Home | Personalized feed |
| 💬 Stream | Topic-based real-time chat (Slack-like) |
| 📋 Forum | Async long-form threads (Discourse-like) |
| ✉️ DMs | 1:1 and group (up to 9) |
| 🤖 Agents | Directory, job board |
| ⚡ Workflows | YAML-as-code automation with traces |
| 🔍 Search | Cmd+K full-text, permission-aware |

## 4. Agent Model — The Differentiator

Buzz treats **agents as first-class members, not bots**:

- Agents have their own Nostr keypairs, their own audit trail, their own channel memberships
- Same affordances as human teammates: open repos, send patches, review code, run workflows, edit canvases, orchestrate other agents, join voice huddles, create channels
- Agent identity follows the Nostr web-of-trust model — persistent npub, verifiable contribution history
- NIP-OA (Owner Attestation): agents inherit access from their human owner

### Agent Toolchain
- **buzz-agent**: ACP (Agent Client Protocol) agent over stdio, calls LLMs, uses MCP tools. Multiple concurrent sessions (up to 8), each with own MCP servers/history/context. Context summarization on overflow.
- **buzz-dev-mcp**: MCP server providing shell + file editor. Ephemeral processes with process-group kill, bounded output.
- **buzz-cli**: agent-first CLI, JSON-only stdout, structured errors on stderr
- **buzz-persona**: persona bundles (model + system prompt). Teams of personas (Ralph for code review, Scout for research, etc.)
- **Remote agents**: deploy to Kubernetes, control via relay (status, steering, shutdown), agent bounds own lifetime

### Agent Protocol Stack
```
ACP Client (Zed, JetBrains, buzz-acp, custom)
  → stdio ACP (JSON-RPC 2.0)
  → buzz-agent (up to 8 concurrent sessions)
    → stdio MCP (JSON-RPC 2.0)
    → buzz-dev-mcp (or any MCP server)
      → shell, str_replace, todo; rg + tree on PATH
```

## 5. Forge — Nostr-Native Git

- Git repos hosted on the relay via Smart HTTP (`git clone`, `git push`)
- NIP-34 repo announcements for discovery
- **Branches are channels**: create a feature branch → Buzz creates a channel. CI, review, merge decision all live there. Branch merges → channel archives into permanent record.
- Branch protections via `buzz-protect` tags in NIP-34 events, enforced at git transport layer
- Approvals are signed Nostr events (kind:46011) — cryptographic proof of who approved what
- NIP-MP (kind:30621) for multi-repo project grouping
- Issues as NIP-34 kind:1621 events, rendered in forum surface
- Docs as collaboratively editable canvases (agents can update via MCP)
- Releases via agent + workflow automation

## 6. Buzz Mesh — Community Compute Pool

A standout feature: community members can **pool idle GPUs** to create a shared AI compute mesh:

- Opt-in sharing of local GPU compute to community
- Models can be split across multiple machines (model parallelism for models too large for one machine)
- Gated by existing community membership — no separate access control
- Built on iroh (relay-mesh transport)
- OpenAI-compatible local endpoint for agents — transparent routing to whoever is serving
- Prompts route directly between machines, relay never sees tokens

## 7. Scale Targets

| Metric | Target |
|--------|--------|
| Users | 10K humans + 50K agents |
| Throughput | ~600K events/day (~7/sec avg) |
| Event store | Postgres 17, partitioned monthly |
| Fan-out | Redis pub/sub, <50ms p99 |
| Search | Postgres FTS, permission-aware |
| Audit | Hash-chain, tamper-evident |

## 8. Status (as of 2026-08)

| Status | Area |
|--------|------|
| ✅ | Core relay, auth, pub/sub, search, audit |
| ✅ | MCP server — full feature surface |
| ✅ | ACP agent harness (Goose, Codex, Claude Code) |
| ✅ | Desktop client (Tauri) — all surfaces |
| ✅ | Channel features — messaging, threads, reactions, canvases, media, editing, deletion, typing |
| ✅ | Workflow engine — YAML-as-code, execution traces, message/reaction/schedule/webhook triggers |
| ✅ | Identity — NIP-05, profiles, NIP-98 auth, agent protection |
| ✅ | Agent CLI, personas, teams |
| ✅ | Huddles — WebSocket Opus voice relay |
| ✅ | Mesh — relay-gated shared AI compute |
| 🚧 | Workflow approval gates (infra exists, executor doesn't persist/resume yet) |
| 🚧 | Mobile client (Flutter, in active dev) |
| 📋 | Remote agents (Kubernetes provider, spec in review) |
| 📋 | Developer portal, push notifications, culture features |

## 9. Relevance to LoopDesk

### Overlapping Concerns
| Area | Buzz | LoopDesk |
|------|------|----------|
| **Agent coordination** | Multi-agent workspace with channels, personas, teams | Loop Engine with maker/checker split, triage, stop conditions |
| **Protocol** | Nostr events (NIP-01) + ACP + MCP | MCP-first, ACP-second adapter layer |
| **State management** | Event log on relay (Postgres) | LOOP-STATE.json (local-first) |
| **Memory/context** | Agent session summarization, relay history search | Durable local memory, session continuity |
| **Workflow** | YAML-as-code automation engine | Loop Engine scheduler |
| **Identity** | Nostr keypairs (secp256k1) | Local workspace identity |
| **Audit** | Hash-chain tamper-evident log | Run log in loop state |

### Key Differentiators — Buzz vs LoopDesk
1. **Buzz is team-first, LoopDesk is personal-first.** Buzz is a multi-user team workspace. LoopDesk is a local-first personal loop workspace for independent developers.
2. **Buzz is a full platform; LoopDesk is a coordination layer.** Buzz replaces Slack + GitHub + CI. LoopDesk keeps context coherent across existing tools (Claude Code, Codex, Trae, Gemini).
3. **Buzz requires infrastructure (Postgres, Redis, S3); LoopDesk is file-based.** Buzz needs a server; LoopDesk runs on your laptop from a JSON file.
4. **Buzz builds its own forge; LoopDesk integrates with existing forges.** Buzz hosts git repos, runs CI, manages issues. LoopDesk adapts to whatever tools you already use.
5. **Buzz's agent model is social (channels, personas, teams); LoopDesk's is procedural (loop, triage, maker/checker).** Different paradigms for different use cases.

### Ideas Worth Borrowing
1. **Agent personas/teams pattern**: the concept of bundling model + system prompt into named personas that can be composed into teams is elegant and could inspire LoopDesk's skill/workflow system.
2. **ACP + MCP clean separation**: Buzz's strict protocol-boundary design (ACP for agent interface, MCP for tools, no coupling) validates LoopDesk's adapter approach.
3. **Context summarization on overflow**: buzz-agent's automatic history summarization for long sessions is directly relevant to LoopDesk's memory/session continuity.
4. **Hash-chain audit log**: tamper-evident run logging could strengthen LoopDesk's run log design.
5. **Community compute mesh**: while out of scope for LoopDesk v0.1, the concept of pooling local compute for agents is forward-looking and worth tracking.

### Risks / Competitive Pressure
- Buzz is backed by Block (Jack Dorsey's company), has 22K stars, and is extremely well-resourced. It could expand into personal-developer territory.
- Buzz's agent toolchain (buzz-agent, buzz-dev-mcp) is production-quality Rust with strong safety guarantees — sets a high bar for agent reliability.
- If Buzz adds a "solo mode" (single-user relay on localhost), it could directly compete with LoopDesk's local-first personal workspace.

### LoopDesk's Moat
- **Local-first simplicity**: no server required, no Postgres, no Redis — just a JSON file and a CLI
- **Tool-agnostic adapter layer**: works across Claude Code, Codex, Trae, Gemini without replacing any of them
- **Loop Engineering methodology**: structured maker/checker/triage/stop-condition execution is a different paradigm from channel-based coordination
- **Worktree isolation**: filesystem-level isolation per loop run, not channel-level isolation
- **Zero social overhead**: no community setup, no relay, no identity ceremony — just start working
