# Module Audit: LoopDesk vs OpenSquilla

> Status: approved
> Last updated: 2026-07-17
> Owner: product/engineering
> Trigger: user request "以LoopDesk为主，尽可能取消OpenSquilla相关模块"
> Authority: AGENTS.md golden rule #1 (LoopDesk owns the v0.1 product surface; legacy OpenSquilla code is runtime library to reuse, not product story to expand) and rule #5 (minimal public surface for v0.1)
> Naming rule: AGENTS.md golden rule #6 (unify LoopDesk / loop_workspace / LOOP-STATE.json / loop CLI; never expose legacy session / workspace-state.json / channel-first copy as v0.1 public naming)

## 1. Summary

LoopDesk v0.1 builds on a runtime originally named **OpenSquilla**. The entire `src/` tree lives under a single Python package `loopdesk` with 31 sub-packages. This audit classifies each module into three categories:

| Category | Definition | Count |
| --- | --- | --- |
| **Cancel** | OpenSquilla legacy; excluded from v0.1 product surface (UI, CLI, docs) | 5 |
| **Retain** | Shared runtime infrastructure; LoopDesk reuses but reframes with LoopDesk design-function descriptions | 16 |
| **Core** | LoopDesk v0.1 product surface; naming and narrative already aligned | 1 package tree |

Cancel modules remain in the source tree as dormant runtime code; they are not deleted, but they must not appear in the CLI, Web UI, docs, or any public-facing surface for v0.1.

## 2. Cancel Modules (Exclude from v0.1 Product Surface)

| Module | OpenSquilla Purpose | Why Cancel for v0.1 | Product Strategy Reference |
| --- | --- | --- | --- |
| `channels/` | 9 IM adapters (Telegram, Discord, Slack, Feishu, DingTalk, QQ, Matrix, MSTeams, WeCom) + WebSocket + Terminal | v0.1 product strategy explicitly defers IM/channel delivery; v0.2 only permits optional channel adapter boundary; channels are multi-user collaboration, not personal loop workspace | §8.2: "Optional IM/channel delivery" is Could Have, not Must/Should; §10 Won't Have: "Multi-user collaboration as the core loop" |
| `scheduler/` | Cron-first scheduling narrative, heartbeat loops, delivery orchestration | Cron is an internal runtime capability (fire-immediately + durable restart), not a user-facing product surface; exposing cron-first scheduling violates the "minimal viable surface" principle | §6: "Loop engineering as product behavior" — local loop scheduling, keep cron as internal runtime only; §8.3: "Local loop scheduling and fire-immediately controls for personal triage; keep cron as an internal runtime capability only and do not expose it as a v0.1 user-facing channel" |
| `migration/` | OpenClaw/Hermes → LoopDesk brand migration scripts | Pure rebranding migration; no functional value for LoopDesk users; LoopDesk has never been OpenClaw or Hermes | Irrelevant to v0.1 scope |
| `squilla_router/` | Token-efficient routing engine using ONNX model inference | "Token-efficient AI agent" is the OpenSquilla value proposition; LoopDesk uses standard LLM provider routing via `provider/` and does not expose routing as a product surface | §8.2: MCP-first + ACP-second cross-tool adapter; routing is runtime plumbing, not a product feature |
| `onboarding/` | Channel configuration wizard and guided setup | Contains `channel_specs.py` and wizard flows heavily oriented toward IM channel setup; LoopDesk onboarding is workspace/project initialization, not channel configuration | §8.6: "Workspace initialization and template selection" — personal workspace, not channel onboarding |

**Implementation rule**: Cancel modules must not have CLI commands (`loopdesk channels`, `loopdesk cron`), Web UI menu entries, RPC endpoints exposed in the gateway, or documentation pages surfaced in `docs/`. They may remain as source code for future v0.2 channel adapter reuse, but all public surface is removed.

### 2.1 Specific Surface Removals

| Surface to Remove | Current Location | Action |
| --- | --- | --- |
| `loopdesk channels` CLI command | `cli/channels_cmd.py` | Remove from CLI registration; do not expose in `--help` |
| `loopdesk cron` CLI command | `cli/cron_cmd.py` (inside scheduler) | Remove from CLI registration |
| `loopdesk sessions` CLI command | `cli/sessions_cmd.py` | Remove; session is renamed to loop workspace state |
| `loopdesk onboard` CLI command | `cli/onboarding_cmd.py` | Remove; replaced by project/workspace init |
| Channel RPC endpoints | `gateway/rpc_channels.py` | Remove from RPC dispatch |
| Channel dispatch logic | `gateway/channel_dispatch.py` | Remove from gateway startup |
| `/channels` Web UI route | `gateway/static/js/` | Remove menu entry and route |
| `/cron` Web UI route | `gateway/static/js/` | Remove menu entry and route |
| `/sessions` Web UI route | `gateway/static/js/` | Remove menu entry and route |
| `docs/channels.md` | `docs/` | Mark as legacy; do not link from LoopDesk docs |
| `docs/cli.md` (channel/cron commands) | `docs/` | Rewrite for LoopDesk CLI only |
| `docs/sessions.md` | `docs/` | Rewrite for LoopDesk workspace state |
| `docs/use-cases.md` | `docs/` | Rewrite entirely — currently all OpenSquilla CLI examples |
| `docs/agents.md` | `docs/` | Rewrite for LoopDesk agent profiles |
| `docs/diagnostics-and-replay.md` | `docs/` | Rewrite for LoopDesk diagnostics |
| `docs/configuration.md` | `docs/` | Rewrite for LoopDesk config |
| `docs/gateway.md` | `docs/` | Rewrite for LoopDesk gateway |
| `README.md` (OpenSquilla brand) | root | Rewrite for LoopDesk brand |
| `README.release.md` | root | Rewrite for LoopDesk release |
| `CONTRIBUTORS.md` (OpenSquilla) | root | Rewrite for LoopDesk |
| `CONTRIBUTING.md` | root | Rewrite for LoopDesk |
| `SUPPORT.md` (OpenSquilla) | root | Rewrite for LoopDesk |
| `CHANGELOG.md` (OpenSquilla) | root | Start fresh LoopDesk changelog section |
| `RELEASES.md` (OpenSquilla) | root | Start fresh LoopDesk releases section |

## 3. Retain Modules (Shared Runtime — LoopDesk Design-Function Descriptions)

Each retained module stays in the source tree but must be reframed with a **OpenSquilla design-function description**: what the module does for the personal loop workspace, stripped of LoopDesk narrative.

### 3.1 `engine/` — Agent Turn Runner

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Agent engine: turn runner, prompt assembly, tool orchestration, sub-agents, hooks |
| LoopDesk design-function | **Loop Goal Execution Runtime**: executes a single Goal turn within a Loop cycle. Assembles prompt from project context + LOOP-STATE + skill instructions, invokes the LLM provider, orchestrates tool calls, and records the result in the run log. Sub-agent spawning and hook execution are Loop-internal mechanisms, not user-facing features. |
| v0.1 surface | Internal runtime; no direct CLI or UI surface (surface goes through Loop Engine, which calls this) |
| Naming change | No Python rename needed; internal. Public narrative: "Loop Goal execution" not "Agent engine" |

### 3.2 `gateway/` — HTTP/WS Server + RPC Dispatch

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Gateway: HTTP/WS server, RPC dispatch, auth, message routing, static UI serving |
| LoopDesk design-function | **LoopDesk Local Control Server**: serves the local Web UI (project view, loop status, approvals, run log), dispatches RPC commands from the UI to the Loop Engine and workspace service, and authenticates local-only access. Channel dispatch, multi-user auth, and IM message routing are removed from v0.1. The server is local-first, not a cloud gateway. |
| v0.1 surface | Serves `/loop-workspace` (project view), `/overview`, `/health`, `/skills`, `/agents`, `/usage`, `/config`, `/logs`, `/approvals` RPC routes. Does NOT serve `/channels`, `/cron`, `/sessions`, `/chat` routes in v0.1. |
| Naming change | `gateway/rpc_loop_workspace.py` stays; `gateway/rpc_channels.py` removed from dispatch; `gateway/channel_dispatch.py` removed from startup |

### 3.3 `cli/` — Command-Line Interface

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Typer CLI app: channels, cron, sessions, agents, gateway, diagnostics |
| LoopDesk design-function | **LoopDesk CLI**: the `loop` command surface. Exposes `opensquilla loop <subcommand>` for workspace init, status, resume, export, goal creation, skill management, and run-log inspection. Legacy `loopdesk channels/cron/sessions/onboard` commands are removed from registration. The binary name should change from `loopdesk` to `loopdesk` in v0.1 packaging. |
| v0.1 surface | `loopdesk loop workspace`, `loopdesk loop status`, `loopdesk loop goal`, `loopdesk loop skill`, `loopdesk loop export`, `loopdesk gateway run` (local server only), `loopdesk health`, `loopdesk diagnostics` |
| Naming change | Binary: `opensquilla` → `loopdesk`; Python package: `opensquilla.cli.loop_workspace_cmd` stays; `cli/channels_cmd.py`, `cli/sessions_cmd.py`, `cli/onboarding_cmd.py` removed from registration |

### 3.4 `tools/` — Built-in Tool Runtime

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Built-in tools: filesystem, shell, web, git, code_exec, skills, media |
| LoopDesk design-function | **LoopDesk Tool Library**: local tools available to Loop Goals during the Maker phase. Each tool is workspace-scoped (path containment, sandbox) and approval-gated for write/external actions. Media tools (image/video generation) are deferred to v0.2 as optional skill extensions, not core v0.1 surface. Core tools: filesystem, shell, web search, git, code execution. |
| v0.1 surface | Internal runtime invoked by Loop Engine during Maker phase; no direct CLI or UI surface for tool management (tools are configured per project in LOOP-STATE.json) |
| Naming change | No rename needed; internal runtime |

### 3.5 `skills/` — Skill Loader and Meta-Skill Orchestrator

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Skill loader, meta-skill orchestrator, skill creator, retrieval embedder |
| LoopDesk design-function | **LoopDesk Skill and Meta-Skill Runtime**: loads project-scoped skills (conventions, review standards, domain knowledge) and meta-skills (repeatable multi-step workflows like dependency review, changelog draft, release check). Skills reduce intent debt across Loop cycles; meta-skills encode reusable Loop Engineering workflows. Skill creation and marketplace are deferred to v0.2. |
| v0.1 surface | `/skills` UI page for browsing and toggling project skills; `loopdesk loop skill` CLI for listing, enabling, disabling |
| Naming change | No rename; narrative shifts from "agent skill" to "LoopDesk project skill" |

### 3.6 `memory/` — Persistent Memory

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Persistent memory: store, embed, refresh, checkpoint, session source |
| LoopDesk design-function | **LoopDesk Project Memory**: durable local storage for project preferences, decisions, reusable facts, failed approaches, and conventions. Memory is project-scoped (tied to a LoopDesk project/workspace, not to a global agent session). Supports keyword and semantic search, compaction for long-running work, and session-to-memory flush so completed Goals become reusable knowledge. |
| v0.1 surface | Internal runtime; `/overview` and project view surface memory stats |
| Naming change | `session source` → `project memory source`; memory root path keyed by project, not by global agent |

### 3.7 `provider/` — LLM Provider Integration

| Attribute | Value |
| --- | --- |
| OpenSquilla name | LLM provider integration (OpenRouter, Anthropic, etc.) |
| LoopDesk design-function | **LoopDesk LLM Provider Layer**: connects to LLM providers for Loop Goal execution. Each project can configure its preferred provider and model. Cost tracking feeds into the Cost Observatory. Provider selection is project-scoped, not global. |
| v0.1 surface | `/config` UI page for per-project provider/model settings; no direct CLI surface |
| Naming change | No rename; narrative: "project-scoped LLM provider" not "agent provider" |

### 3.8 `mcp/` — Outbound MCP Client

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Outbound MCP client (SSE, stdio transports) |
| LoopDesk design-function | **LoopDesk MCP Adapter (Outbound)**: connects to external coding tools (Claude Code, Codex, Codebuddy, Trae, Gemini) via MCP protocol. Translates outbound workspace state into tool-ready input, and receives tool results back into LOOP-STATE. This is the core v0.1 cross-tool adapter layer — MCP-first per product strategy §6. |
| v0.1 surface | Internal runtime invoked by Loop Engine; `/config` shows connected MCP servers per project |
| Naming change | No rename; this is already the LoopDesk adapter core |

### 3.9 `mcp_server/` — Inbound MCP Server Bridge

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Inbound MCP server bridge (exposes OpenSquilla sessions to external MCP clients) |
| LoopDesk design-function | **LoopDesk MCP Server (Inbound)**: exposes the LoopDesk workspace state and tool surface to external MCP clients, so other tools can call LoopDesk as an MCP server. This enables cross-tool bidirectional integration — other AI tools can query LoopDesk project state, invoke LoopDesk skills, and receive structured results. v0.1 keeps this for `loopdesk_mcp.py` entry point. |
| v0.1 surface | `loopdesk_mcp.py` script; no direct UI surface |
| Naming change | `OpenSquillaMCPBridge` → `LoopDeskMCPBridge` in class name; `clientInfo.name` from `"opensquilla"` to `"loopdesk"` |

### 3.10 `safety/` — Injection Protection, Permission Matrix, Sandbox Policy

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Injection protection, permission matrix, tool hierarchy, sandbox policy |
| LoopDesk design-function | **LoopDesk Safety Guard**: protects the personal loop workspace from prompt injection, unauthorized tool calls, and runaway automation. Enforces per-project permission matrices (read-only / restricted / full-access modes), tool call approval gates, denylist paths, and escalation triggers for ambiguous or repeated-failure situations. This is the enforcement layer behind the Cost Observatory and Safety Guard core feature (feature list §7). |
| v0.1 surface | `/approvals` UI page for pending approval queue; escalation notifications in project view |
| Naming change | No rename; narrative: "project safety guard" not "agent safety" |

### 3.11 `sandbox/` — Sandbox Execution

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Sandbox execution (bubblewrap/seatbelt backends), workspace containment |
| LoopDesk design-function | **LoopDesk Worktree Isolation Sandbox**: provides per-Goal worktree isolation for risky or automated work. Uses OS-level sandbox backends (bubblewrap on Linux, seatbelt on macOS) to enforce path containment, network restrictions, and resource limits. Supports cleanup or audit snapshot retention after Goal completion. This implements feature list §8 (Worktree Isolation). |
| v0.1 surface | Internal runtime; no direct UI surface (worktree status shown in project view run log) |
| Naming change | No rename; narrative: "project worktree sandbox" not "agent sandbox" |

### 3.12 `identity/` — Agent Identity Resolution

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Agent identity resolution (AGENTS.md, SOUL.md, IDENTITY.md); workspace file loader |
| LoopDesk design-function | **LoopDesk Project Identity Loader**: reads project-level identity files (AGENTS.md, SOUL.md, IDENTITY.md, USER.md) from the project root directory to configure the Loop's behavior, personality, and boundaries for that project. Identity is project-scoped, not global — each project can have different agent profiles, preferences, and constraints. |
| v0.1 surface | Internal runtime; `/agents` UI page for browsing project agent profiles |
| Naming change | Narrative: "project identity" not "agent identity"; file loading stays compatible with existing format |

### 3.13 `session/` — Session Model (Legacy Naming)

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Session model with ChatType.CHANNEL, QueueMode, SendPolicy, channel key builders |
| LoopDesk design-function | **LoopDesk Workspace State Model**: provides the durable state model for a LoopDesk project/workspace. Each project has its own state (loop phase, active goals, run log, cost rollup). The ChatType.CHANNEL enum and channel key builders are removed from v0.1; the model is refactored to use LoopDesk naming (LoopPhase, GoalState, ProjectKey). The session-to-memory flush mechanism is retained but reframed as "Goal completion → project memory flush". |
| v0.1 surface | Internal model; no direct CLI/UI surface named "session" (surface is project view and loop status) |
| Naming change | **Critical**: `ChatType.CHANNEL` → remove; `build_channel_key()` → remove; `SessionManager` → `LoopWorkspaceService` (already exists in `loop_workspace/`); `session` CLI → removed; `sessions` UI → removed; all public naming must use `loop_workspace` / `project` / `loop` per AGENTS.md #6 |

### 3.14 `chat/` — Chat Interaction and Streaming

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Chat interaction, streaming, message rendering |
| LoopDesk design-function | **LoopDesk Task Interaction Layer**: provides the interaction surface for creating and continuing tasks within a project. In v0.1, this is reframed as "新建任务" (New Task) per the IA redesign — each task belongs to a project, maintains its own context, and follows Loop Engineering phases (triage → maker → checker → escalation → run log → stop). The chat streaming mechanism is reused for task interaction, but the narrative is task/project-scoped, not free-floating chat. |
| v0.1 surface | "新建任务" in sidebar; task creation requires project selection; task view shows Loop Engineering phase tracker |
| Naming change | UI label: "对话/Chat" → "新建任务/New Task"; internal streaming code stays; narrative reframed |

### 3.15 `agents/` — Runtime Agent Profiles

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Runtime agent profiles (named configuration for agent behavior) |
| LoopDesk design-function | **LoopDesk Project Agent Profiles**: project-scoped configurations that define how the Loop behaves for a specific project — which tools are available, which skills are enabled, what the permission mode is, and what the agent identity (SOUL.md / IDENTITY.md) says. Profiles are project-scoped, not global; switching projects switches the entire agent profile. |
| v0.1 surface | `/agents` UI page for browsing and editing project agent profiles |
| Naming change | Narrative: "project agent profile" not "global agent" |

### 3.16 `dist/` — Distribution Manifest (Naming Conflict)

| Attribute | Value |
| --- | --- |
| OpenSquilla name | Distribution manifest: `workspace-state.json` builder, `BUNDLED_CHANNELS` |
| LoopDesk design-function | **LoopDesk Distribution Manifest**: provides the initial state template for new LoopDesk projects. The naming conflict must be resolved: `workspace-state.json` → `LOOP-STATE.json`, and `BUNDLED_CHANNELS` → removed (channels are not v0.1). The manifest builder generates project-initialization templates (LOOP-STATE.json, memory/, skills/, artifacts/, worktrees/) per the product strategy §8 Scenario D (workspace initialization and template selection). |
| v0.1 surface | Internal distribution; no direct UI surface |
| Naming change | **Critical**: `workspace-state.json` → `LOOP-STATE.json`; `BUNDLED_CHANNELS` → removed; `WorkspaceStateBuilder` → `LoopDeskProjectInitBuilder` |

## 4. Core Module (LoopDesk Product Surface)

| Module | Purpose | v0.1 Status |
| --- | --- | --- |
| `loop_workspace/` | Personal loop workspace: LOOP-STATE.json schema, layout, service, engine (triage/maker/checker), MCP adapters, CLI bridge, RPC handlers, JS frontend, worktree, memory index, templates | Fully implemented; naming aligned; v0.1 core entry |

Sub-packages within `loop_workspace/` that are v0.1 product surface:

| Sub-package | LoopDesk Design-Function |
| --- | --- |
| `loop_workspace/schema.py` | `LOOP-STATE.json` schema definition |
| `loop_workspace/layout.py` | Project directory structure (memory, skills, artifacts, worktrees) |
| `loop_workspace/service.py` | `LoopWorkspaceService` — project state lifecycle |
| `loop_workspace/engine/` | Loop Engine state machine (triage → maker → checker → escalation → run log → stop) |
| `loop_workspace/adapters/` | MCP client adapter, inbound/outbound event translators |
| `loop_workspace/mcp.py` | MCP integration for cross-tool adapter |
| `loop_workspace/scripts/loopdesk_mcp.py` | External MCP server entry point |
| `loop_workspace/worktree.py` | Per-Goal worktree isolation |
| `loop_workspace/memory_index.py` | Project-scoped memory search index |

## 5. Additional Shared Runtime Modules (No Product Surface)

These modules are internal plumbing with no direct product surface. They stay as-is, reframed in LoopDesk narrative only if mentioned in docs.

| Module | LoopDesk Reframing |
| --- | --- |
| `compat/` | Compatibility shim (aiosqlite); no narrative change needed |
| `contracts/` | Contract types; no narrative change needed |
| `contrib/` | Contributed code; no narrative change needed |
| `health/` | **LoopDesk Health Check** — runtime health for local desktop server |
| `observability/` | **LoopDesk Diagnostics & Replay** — run diagnostics and state replay for debugging bad loops |
| `persistence/` | Data persistence utilities; no narrative change needed |
| `plugins/` | Plugin system (tokenjuice compaction); no narrative change needed |
| `search/` | **LoopDesk Web Search Tool** — local web search provider, shared runtime for Loop Goals |
| `application/` | Partially retained: approval queue and intent cache are LoopDesk-relevant; wizard.py is legacy and removed from v0.1 surface |

## 6. Naming Conflict Resolution Plan

| Conflict | Current | Resolution | Scope |
| --- | --- | --- | --- |
| Package name | `opensquilla` (pyproject.toml) | `loopdesk` in packaging; Python source stays as `opensquilla` for v0.1 to avoid massive import rewrite, but public-facing names (binary, env vars, docs) all switch to `loopdesk` | v0.1 public surface only |
| Binary name | `opensquilla` (CLI entry point) | `loopdesk` — alias `opensquilla` as compat fallback for one release | v0.1 CLI |
| Env vars | `OPENSQUILLA_*` | `LOOPDESK_*` — `OPENSQUILLA_*` accepted as compat fallback | v0.1 config |
| Config file | `opensquilla.toml.example` | `loopdesk.toml.example` — compat fallback reads old name | v0.1 config |
| Docker image | `opensquilla:local` | `loopdesk:local` | v0.1 compose |
| State file | `workspace-state.json` (in dist/) | `LOOP-STATE.json` (already exists in project root); dist builder renamed | v0.1 |
| Session naming | `opensquilla sessions` CLI, `SessionManager` | Removed from CLI; `LoopWorkspaceService` replaces for public surface | v0.1 |
| Channel naming | `ChatType.CHANNEL`, `build_channel_key()` | Removed from v0.1 public model | v0.1 |
| MCP client info | `{"name": "opensquilla"}` | `{"name": "loopdesk"}` | v0.1 MCP |
| Class name | `OpenSquillaMCPBridge` | `LoopDeskMCPBridge` | v0.1 source |

**Note on Python import path**: v0.1 时期为避免 300+ 文件重写破坏 runtime，先只做 public surface 命名统一；internal Python imports 暂留 `opensquilla`。Q23 / v1.0+ 已确认立即启动全量迁移；当前 `docs/decisions/full-package-rename.md:1` 是生效决策，主仓库应继续向 `loopdesk` 全量推进，而不是回退到只改公共命名。

## 7. Module Surface Map (v0.1)

This is the definitive v0.1 surface map. Anything not listed here is internal runtime with no user-facing surface.

| Surface | Module | LoopDesk Label |
| --- | --- | --- |
| **CLI binary** | `cli/` | `loopdesk` |
| **CLI subcommands** | `cli/loop_workspace_cmd.py` | `loopdesk loop workspace`, `loopdesk loop status`, `loopdesk loop goal`, `loopdesk loop skill`, `loopdesk loop export` |
| **CLI gateway** | `cli/gateway_cmd.py` | `opensquilla gateway run` |
| **CLI health** | `cli/health_cmd.py` | `loopdesk health` |
| **Web UI: Project View** | `gateway/static/js/views/loop_workspace.js` | 工作台 (Workspace) |
| **Web UI: Overview** | `gateway/static/js/views/` | 总览 (Overview) |
| **Web UI: Health** | `gateway/static/js/views/` | 健康 (Health) |
| **Web UI: Skills** | `gateway/static/js/views/` | 技能 (Skills) |
| **Web UI: Agents** | `gateway/static/js/views/` | 代理 (Agents) |
| **Web UI: Usage** | `gateway/static/js/views/` | 用量 (Usage) |
| **Web UI: Config** | `gateway/static/js/views/` | 配置 (Config) |
| **Web UI: Logs** | `gateway/static/js/views/` | 日志 (Logs) |
| **Web UI: Approvals** | `gateway/static/js/views/` | 审批 (Approvals) |
| **Web UI: New Task** | `chat/` + `gateway/static/js/views/` | 新建任务 (New Task) |
| **MCP server** | `loop_workspace/scripts/loopdesk_mcp.py` | LoopDesk MCP Server |
| **State file** | `LOOP-STATE.json` (project root) | LoopDesk Project State |

**NOT in v0.1 surface**: channels, cron, sessions, onboarding, squilla_router, migration, wizard, workspace-state.json, loopdesk binary name

## 8. Open Items

1. **`docs/web-ui.md`**: Still contains OpenSquilla multi-channel console narrative. Must be rewritten or marked as legacy per this audit.
2. **`docs/use-cases.md`, `docs/agents.md`, `docs/diagnostics-and-replay.md`, `docs/configuration.md`, `docs/gateway.md`**: All written entirely in OpenSquilla CLI terminology. Must be rewritten for LoopDesk.
3. **`application/wizard.py`**: OpenSquilla brand wizard; remove from v0.1 surface. Approval queue (`application/approval_queue.py`) and intent cache (`application/intent_cache.py`) are retained.
4. **Full Python package rename**: Deferred to post-v0.1. v0.1 uses `loopdesk` for all public names while keeping `loopdesk` as the internal Python package path.
5. **`pyproject.toml`**: Package name stays `loopdesk` for v0.1 internal compatibility; add `loopdesk` as the public-facing binary/script name.

---

This audit is the authoritative reference for any v0.1 surface, naming, or module-scope decision. When in doubt, refer to AGENTS.md golden rules #1, #5, and #6, and this document.
