# Competitive Intelligence — Zleap-Agent (Zleap-AI/Zleap-Agent)

> Research date: 2026-07-09
> Source: public GitHub repo `Zleap-AI/Zleap-Agent` (depth-1 clone), README, source code inspection of all packages, database schema, architecture patterns.
> Audience: LoopDesk product/engineering planning for personal-loop workspace targeting independent developers.

## 1. Research Method

- Cloned `https://github.com/Zleap-AI/Zleap-Agent` and inspected full monorepo structure (~481 TypeScript files, ~115,000 lines).
- Analyzed all 12 packages: `agent`, `ai`, `avatar`, `cli`, `core`, `desktop`, `gateway`, `host`, `runtime`, `store`, `tasks`, `web`.
- Read database schema (main schema + core event graph schema), kernel/workspace/turnLoop engine source, memory dream system, tool definitions, MCP runtime, conversation service, task service, permission system, gateway platforms, and web UI API routes.
- Cross-referenced with LoopDesk product positioning and existing competitive research.

## 2. Product Identity

### 2.1 Positioning
- **Tagline**: "Workspace Is All Agents Need"
- **Core promise**: context isolation via workspaces. An agent should not see every tool, memory, rule, and previous message on every step — it should receive only context relevant to its current workspace.
- **Status**: early preview, not production-released. License not yet finalized.

### 2.2 Target User
- Developers and teams running local or OpenAI-compatible models who want structured agent workflows with workspace-level isolation.
- Emphasis on smaller local models (where context overflow is a real problem) and enterprise-local deployments where permissions and data boundaries matter.

### 2.3 Differentiation Claim
- Workspace-first architecture: each workspace has its own prompt, tools, skills, memory, model, and execution history.
- Not just a chat wrapper — a runtime with workspace routing, memory partitioning, and task scheduling.

## 3. Architecture Overview

### 3.1 System Shape
- **Monorepo** (pnpm workspaces, 12 packages, ~481 TS files, ~115K lines).
- **packages/agent**: core agent runtime — kernel, workspace definitions, turn loop, tools, memory dream, MCP runtime, compaction, artifact sources.
- **packages/ai**: model provider abstraction — OpenAI-compatible + Anthropic providers, streaming, embeddings.
- **packages/avatar**: run assembly for inbound/scheduled/web-chat entry points.
- **packages/cli**: terminal UI and CLI entrypoint.
- **packages/core**: shared types, runtime types, skill definitions, memory orchestrator types, agent runtime abstraction.
- **packages/desktop**: Tauri desktop app (planned/early).
- **packages/gateway**: IM gateway workers for Feishu, WeChat, and Feishu CLI long-connection.
- **packages/host**: local supervisor, Postgres bootstrap, install/update helpers.
- **packages/runtime**: runtime-facing workspace and conversation APIs.
- **packages/store**: PostgreSQL storage, migrations, event graph, recall logic.
- **packages/tasks**: scheduled task service, cron, queue, workers.
- **packages/web**: Next.js 16 Web UI (App Router + React 19 + Tailwind CSS v4 + shadcn/ui).

### 3.2 Database
- **PostgreSQL with pgvector** — required dependency, not optional.
- Rich schema (~30+ tables) covering:
  - `avatars` + `avatar_versions`: agent identity and versioning.
  - `spaces` + `space_versions`: global workspace definitions with versioned instructions, routing cards, model bindings.
  - `capability_definitions` + `space_capability_bindings`: deterministic tool/skill binding per workspace version.
  - `skill_definitions`: reusable skill packages with trust status, risk audit, tool policies.
  - `threads` + `thread_entries`: conversation persistence with structured session entries.
  - `agent_memory`: impression (person) and experience memory per agent/user.
  - `model_configs`: stored model provider configurations.
  - `mcp_servers` + `mcp_tool_definitions`: MCP server registry with per-server secrets management.
  - `artifacts` + `artifact_references`: generated artifact storage.
  - `runtime_cache_entries`: temporary workspace-level cache for tool results.
  - `ledger_events`: audit trail for all run/work/step events.
  - `sessions` + `session_runs`: session lifecycle tracking.
  - **Core event graph** (5 tables): `source_group`, `source`, `event`, `entity`, `event_entity` — with vector embeddings, keyword search, entity extraction, and relationship tracking.

### 3.3 Agent Runtime
- **Kernel**: workspace-entry kernel. Every reply enters the resident `main` space, where the session model routes to a work space via `switchWorkspace(space, task)`.
- **Turn loop**: up to 200 tool iterations per workspace step. Loop discipline enforced via system prompt: "prefer acting with tools over narrating."
- **Workspace model**: "Zleap works like an operating system. Main is the desktop; workspaces are app windows."
- **Built-in tools**: `get_time`, `ls`, `read`, `find`, `grep`, `write`, `append`, `edit`, `bash`, `web_search`, `web_read`, `switchWorkspace`, `finishTask`, `readMessage`, `task_manage`, `findSkill` — plus MCP runtime tools.
- **Tool approval**: two modes — `request_approval` (high-risk tools require HITL confirmation) and `full_access`.
- **Artifact system**: automatic detection and tracking of generated files with diff snapshots.

### 3.4 Memory System (Three Layers)
1. **Person memory** (impressions): user preferences and stable user facts, scoped per agent+user.
2. **Event memory** (work records): facts and state related to a user, task, or workspace — stored in the core event graph with vector embeddings, entity extraction, and relationship tracking.
3. **Experience memory**: reusable methods learned from completed work — global per agent, not user-scoped.

**Memory Dream**: background process that periodically reviews completed sessions (minimum 3 sessions or 20 tool events), extracts experience memories via LLM, and reconciles person profiles. Runs on a configurable schedule (default: once per 24 hours).

**Compaction**: when conversation history grows long, older messages are folded into summaries and extracted into the record event graph, preserving knowledge while freeing context window.

### 3.5 Skill System
- Skills are `SKILL.md`-centered packages with instructions, tool bindings, files, and resources.
- Skills can have trust status, risk audit, invocation policy, and tool allow/disallow lists.
- Web UI supports skill import, scanning, and a marketplace concept.
- Skills are bound to workspaces via `space_capability_bindings`.

### 3.6 Task Scheduling
- Cron-based scheduled tasks with timezone support.
- Task types: `agent` (prompt-driven), custom types.
- Task runs with status tracking: queued, running, completed, failed, skipped.
- Stale run reclamation (default: 1 hour timeout).
- Manual trigger support (`runNow`).

### 3.7 IM Gateway
- Feishu (Lark), WeChat, and Feishu CLI long-connection platforms.
- Message deduplication, platform-specific normalization.
- Group policy control (open/disabled/allowed users).
- Docker Compose profile for independent gateway worker.

### 3.8 Web UI
- Next.js 16 + React 19 + Tailwind CSS v4 + shadcn/ui + radix-ui.
- Full management UI for: chat, workspaces, assistants (avatars), models, tools, MCP servers, skills, memory, tasks, artifacts, gateway configuration.
- API routes for: chat, conversations, spaces, tools, MCP, models, skills, tasks, memory, artifacts, projects, avatar, integrations, preferences.
- Design language: "neutral chassis + copper-gold/amber accent; cardless-first."

### 3.9 Model Support
- OpenAI-compatible provider as primary (any OpenAI-compatible API).
- Anthropic provider code present.
- Per-workspace model binding: different workspaces can use different models.
- Model configuration stored in database with test connectivity support.

## 4. Core Capabilities Summary

| Capability | Details |
| --- | --- |
| **Workspace isolation** | Separate prompt, tools, skills, memory, model, history per workspace |
| **Workspace routing** | Main space routes to work spaces via `switchWorkspace`; depth-1 architecture |
| **Three-layer memory** | Person (impressions) + Event (work records with embedding search) + Experience (reusable learned methods) |
| **Memory Dream** | Background LLM-driven memory extraction from completed sessions |
| **Context compaction** | Automatic folding of old history into summaries + record extraction |
| **MCP support** | Full MCP server/tool registry with secret management |
| **Skill system** | SKILL.md packages with trust/risk audit, tool policies, workspace binding |
| **Task scheduling** | Cron-based with timezone, manual trigger, stale reclamation |
| **IM gateway** | Feishu/WeChat long-connection integration |
| **Built-in tools** | File ops, bash, web search/read, grep, workspace control |
| **Artifact tracking** | Automatic file-change detection and diff snapshots |
| **CLI** | Terminal UI with same runtime as Web UI |
| **Web UI** | Full Next.js management interface |
| **Permission modes** | request_approval / full_access |
| **Multi-model** | Per-workspace model binding, OpenAI-compatible + Anthropic |
| **Audit trail** | Ledger events for all run/work/step lifecycle |

## 5. Competitive Comparison with LoopDesk

### 5.1 Overlap Areas

| Dimension | Zleap-Agent | LoopDesk (v0.1 plan) |
| --- | --- | --- |
| Workspace isolation | ✅ Core feature (prompt/tools/skills/memory/model per space) | ✅ Planned (worktree isolation per task) |
| Memory system | ✅ Three-layer (person/event/experience) with vector search + Memory Dream | ✅ Planned (durable local memory) |
| Skills | ✅ SKILL.md packages with trust/risk audit | ✅ Planned (reusable workflow knowledge) |
| Task scheduling | ✅ Cron-based with timezone | ◯ Not explicitly in v0.1 scope |
| MCP support | ✅ Full server/tool registry | ✅ Planned (MCP adapter layer) |
| CLI | ✅ Terminal UI | ✅ Planned (`loop` CLI) |
| Web UI | ✅ Full Next.js management UI | ✅ Planned (minimal local Web UI) |
| Cost tracking | ◯ Usage in ledger events but no explicit cost controls | ✅ Planned (cost/safety controls) |
| Local-first | ⚠️ Requires PostgreSQL+pgvector | ✅ Local-first, no mandatory server |

### 5.2 Key Differentiation

| Dimension | Zleap-Agent | LoopDesk |
| --- | --- | --- |
| **Core mental model** | Workspace-as-OS: Main desktop + work app windows | Personal loop workspace: context coherence engine |
| **Primary value** | Context isolation per workspace (especially for smaller/local models) | Keep loop state coherent across multiple external AI tools |
| **Multi-tool orchestration** | Single agent runtime with internal workspace routing | Cross-tool adapter layer spanning Claude Code, Codex, Trae, Gemini, etc. |
| **Architecture** | Monolithic agent runtime (one agent, many workspaces) | Meta-layer orchestrating multiple external agents |
| **Loop engineering** | Turn loop with tool iterations, but no triage/maker/checker/escalation methodology | First-class: triage → maker → checker → escalation → run log → stop condition |
| **Workspace state protocol** | PostgreSQL schema (internal, not portable) | LOOP-STATE.json (structured, portable, tool-readable) |
| **Database dependency** | PostgreSQL+pgvector required | No database requirement (local-first) |
| **Memory sophistication** | Very advanced: 3-layer memory + event graph + vector search + entity extraction + Memory Dream | Planned durable memory (simpler) |
| **Model routing** | Per-workspace model binding built-in | Not primary — tools bring their own models |
| **IM integration** | Feishu/WeChat gateway | Not in scope |
| **Cross-device** | No cross-device support | Not in scope (both local-first) |
| **Provider integration** | OpenAI-compatible + Anthropic (direct model calls) | MCP/ACP adapter wrapping external coding agents |

### 5.3 What Zleap-Agent Does Well

1. **Workspace isolation architecture**: treating context as `System Prompt + Workspace Prompt + Tools + Memory + History` with per-workspace isolation is conceptually clean and practically useful for context window management.
2. **Memory system depth**: three-layer memory (person/event/experience) with the core event graph (entities, embeddings, keyword search, relationship tracking) is the most sophisticated memory system among competitors analyzed so far.
3. **Memory Dream**: scheduled background extraction of experience memories from completed sessions is a novel approach to accumulating reusable knowledge.
4. **Context compaction**: automatic folding of old messages into summaries + record extraction balances context window limits with knowledge preservation.
5. **Skill system with trust/risk audit**: skills carry security metadata (trust status, risk audit, tool allow/disallow lists) — a practical enterprise concern.
6. **Per-workspace model binding**: different models for different workspaces is a strong cost/capability optimization.
7. **MCP integration**: full server/tool registry with secret management makes external tool connection first-class.
8. **Comprehensive Web UI**: full management surface for all system aspects (workspaces, models, skills, memory, tasks, MCP, artifacts).
9. **Turn loop discipline**: "prefer acting with tools over narrating" + tool reason requirements + 200-iteration budget is a thoughtful approach to agent reliability.
10. **Audit trail**: ledger events for full run/work/step lifecycle provide observability.

### 5.4 What Zleap-Agent Over-Delivers On (relative to LoopDesk's target user)

1. **IM gateway**: Feishu/WeChat integration is specific to Chinese enterprise use cases, outside LoopDesk's personal-first scope.
2. **Single-agent depth**: Zleap-Agent IS the agent; LoopDesk orchestrates existing agents (Claude Code, Codex, etc.). Independent devs already have their preferred coding agents.
3. **Database complexity**: PostgreSQL+pgvector requirement is heavy for a personal tool. 30+ tables, vector indexes, and entity graphs add operational burden.
4. **Avatar/persona system**: multiple agent personas with versioning is a team/enterprise feature beyond personal use.

### 5.5 What Zleap-Agent Under-Delivers On (relative to LoopDesk's target user)

1. **No cross-tool continuity**: Zleap-Agent is a self-contained agent runtime, not a layer that connects existing tools. It cannot keep context coherent across Claude Code, Codex, or Trae — it replaces them.
2. **No loop engineering methodology**: the turn loop is a tool-call iteration loop, not a triage → maker → checker pattern. No structured escalation, no explicit stop conditions beyond tool iteration limits.
3. **No portable workspace state**: all state is in PostgreSQL. No `LOOP-STATE.json` or equivalent that other tools can read. State is not portable or tool-readable.
4. **No git worktree isolation**: workspaces are context isolation boundaries, not filesystem isolation. Multiple workspaces share the same file system root.
5. **No cost controls**: no token budgets, cost limits, or cost-aware model routing. Usage is tracked in the ledger but not enforced.
6. **Heavy infrastructure**: requires Docker Desktop (or a reachable PostgreSQL+pgvector instance). Not a "download and run" experience for personal use.
7. **Early maturity**: preview status, no finalized license, rapidly changing APIs. LoopDesk's v0.1 plan, while unimplemented, is more deliberatively designed.

## 6. Threat Assessment

### 6.1 Direct Competitive Threat: Low-Medium

Zleap-Agent and LoopDesk solve **fundamentally different problems**:
- Zleap-Agent: "I am your agent runtime with intelligent workspace routing" (replaces your coding agent).
- LoopDesk: "I keep your existing agents coherent" (orchestrates your coding agents).

An independent developer who already uses Claude Code + Codex would not switch to Zleap-Agent as a replacement. They would use LoopDesk to keep those tools coherent.

However, if Zleap-Agent's workspace isolation and memory system become mature and usable, it could attract developers looking for a single integrated agent experience — reducing the multi-tool audience that LoopDesk targets.

### 6.2 Risk: Zleap-Agent's Memory System Sets User Expectations

- Zleap-Agent's three-layer memory with Memory Dream and event graph could become a reference implementation for what "agent memory" means.
- If LoopDesk's memory system is significantly simpler (e.g., flat key-value), users who've seen Zleap's approach may perceive LoopDesk's memory as insufficient.
- **Mitigant**: LoopDesk's memory serves a different purpose (cross-tool continuity, not within-agent recall). The requirements are genuinely different.

### 6.3 Risk: Workspace Isolation Concept Confusion

- Both products use "workspace" as a key concept but mean different things:
  - Zleap: workspace = context isolation boundary within one agent.
  - LoopDesk: workspace = personal loop workspace spanning multiple agents.
- **Mitigant**: clear positioning and naming. LoopDesk uses `loop_workspace` / `LOOP-STATE.json` to differentiate.

### 6.4 Opportunity: Borrow Memory Architecture Patterns

- Zleap-Agent's separation of person/event/experience memory is conceptually transferable.
- The Memory Dream pattern (periodic background extraction of reusable knowledge from completed sessions) is directly applicable to LoopDesk's cross-tool memory needs.
- The compaction + record extraction pattern (fold old context, extract knowledge into durable storage) is relevant for LoopDesk's session history management.

## 7. Takeaways for LoopDesk v0.1

1. **LoopDesk's meta-layer positioning is safe.** Zleap-Agent replaces coding agents; LoopDesk orchestrates them. These are complementary, not competing, for multi-tool developers.

2. **Design memory with category separation.** Zleap's person/event/experience split is well-reasoned. LoopDesk's memory system should at minimum distinguish:
   - **User preferences**: cross-session personal context (like Zleap's person memory).
   - **Task state**: per-task facts and decisions (like Zleap's event memory).
   - **Learned methods**: reusable patterns extracted from completed work (like Zleap's experience memory).
   Even if the implementation is simpler (local files vs. PostgreSQL+pgvector), the conceptual separation matters.

3. **Consider a Memory Dream equivalent.** Periodic background extraction of reusable knowledge from completed loops is a powerful pattern that maps naturally to LoopDesk's loop-end run log. When a loop completes, extract what was learned into durable skills/knowledge.

4. **Keep infrastructure lightweight.** Zleap-Agent's PostgreSQL+pgvector+Docker requirement is a real adoption barrier for personal use. LoopDesk's local-first, zero-infrastructure approach is a genuine advantage. Do not add database dependencies for v0.1.

5. **Workspace state portability remains a differentiator.** Zleap locks all state in PostgreSQL — opaque to other tools. `LOOP-STATE.json` as a portable, human-readable, tool-readable state file is a unique value proposition that no competitor offers.

6. **Loop engineering is still the moat.** Zleap has a turn loop (iterate tool calls until done) but no structured methodology. Triage → maker → checker → escalation → run log → stop condition remains LoopDesk's unique approach that no competitor has replicated.

7. **Watch workspace routing as a pattern.** Zleap's "Main dispatches to work spaces" is conceptually similar to LoopDesk's "triage decides what runs next." If LoopDesk's Loop Engine includes intelligent routing (which tool/agent for which sub-task), it echoes this pattern but at a higher abstraction level (across tools, not within one agent).

8. **Borrow the good patterns:**
   - Tool reason requirements (`requiresReason: true`) for audit/trace quality.
   - Turn loop discipline: "a turn with no tool call is the final answer" prevents indefinite narration.
   - Skill trust/risk audit metadata for safety controls.
   - Compaction as a memory pattern: fold old context into summaries + durable records.
   - Ledger events for full lifecycle audit trail.
