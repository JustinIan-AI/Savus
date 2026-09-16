# PRD — LoopDesk Personal Loop Workspace

> Status: Draft for Review
> Version: v1.0
> Owner: Product / Engineering
> Last updated: 2026-07-16
> Sources: `docs/decisions/product-strategy.md`, `docs/decisions/desktop-web-im-product-boundary.md`, `docs/architecture/personal-loop-workspace.md`, `docs/research/competitive-intel.md`, `docs/research/competitive-intel-proma.md`, `docs/features/core-feature-list.md`, `docs/releases/loopdesk-v0.1.md`, `docs/releases/loopdesk-v0.2.md`, `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`, `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md`, `docs/decisions/v0.2-channel-adapter.md`

## 1. Purpose

This PRD defines the complete product direction for LoopDesk as a **desktop-first personal loop workspace** with a **lightweight web surface for distribution, inspection, guided setup, and diagnostics**, and **optional IM-driven remote control for resuming approved workspace work from a trusted chat workspace**.

LoopDesk helps one developer keep context, memory, loop state, and execution coherent across Claude Code, Codex, Codebuddy, Trae, Gemini, and similar tools. The desktop app is the primary runtime. The web surfaces are secondary delivery and control layers. IM is a continuation surface, not a replacement for the local workspace.

## 2. Background

Independent developers increasingly juggle multiple AI tools in one project. Existing competitors each solve only part of the problem:
- Tutti-like shared context handoff, but without durable portable state.
- WeSight/Orca-like local runtime visibility, but inside heavy desktop shells or IDE wrappers.
- Happier/cc-connect-like remote control and channel breadth, but without explicit loop engineering or local-first state ownership.
- Proma-like local-first Chat/Agent workbench, workspace Skills/MCP, and remote bot bridges, but centered on its own desktop workflow shell rather than durable cross-tool loop continuity.

LoopDesk should own the missing layer: a **portable personal loop workspace** where the developer's next action, prior decision, and current execution state are inspectable across tools without forcing a single vendor shell, cloud room, or SaaS runtime.

## 3. Goals and Non-Goals

### 3.1 Goals
- Reduce context re-entry cost when switching between AI tools.
- Provide one durable workspace for tasks, memory, skills, artifacts, loop state, and worktree isolation.
- Make the desktop app the primary runtime for installation, gateway hosting, file access, agent orchestration, and richest inspection.
- Use web surfaces for guided install, workspace inspection, approvals, diagnostics, and operator setup.
- Use IM as a lightweight continuation surface to choose a workspace, resume approved work, approve/reject actions, and receive compact status updates.
- Enable loop-driven automation with safety, cost control, local observability, and explicit stop conditions.
- Keep the product personal, local-first, portable, and inspectable.

### 3.2 Non-Goals
- Build a general team collaboration suite.
- Replace Claude Code, Codex, Codebuddy, Trae, or Gemini.
- Make IM the primary loop runtime or narrative.
- Force cloud sync, cloud rooms, or multi-user workspaces as core requirements；LoopDesk does not take this direction.
- Ship a heavy IDE with broad creator/media/team features.

## 4. Target Users

### 4.1 Primary User
- Independent developer who codes, documents, reviews, and ships alone or with a small set of AI tools.

### 4.2 Secondary Users
- Operator-developer who wants to inspect runs, approve actions, and triage alerts from another device without moving back to the desktop.
- Power user who wants cross-device continuation for bounded, already-approved work items.

### 4.3 User Needs
- Start work on one machine and resume it from the same desktop or a trusted remote surface.
- Choose a workspace and continue an approved task from IM without re-explaining full context.
- Inspect loop state, run log, memory, skills, approvals, and cost in one place.
- Keep work portable and recoverable without proprietary cloud lock-in.
- Run risky or repeatable loops safely with worktree isolation, approvals, and kill conditions.

## 5. Product Narrative

### 5.1 Product Promise
- Start a task in any supported coding agent.
- Continue it from desktop, web, or an approved IM workspace without copy-pasting full context.
- See the current loop state, not only the latest chat message.
- Let LoopDesk suggest the next safe action, surface cost, and record the outcome.
- Keep sessions, decisions, artifacts, and run history in one searchable personal workspace.

### 5.2 Positioning Statement
For independent developers who move between Claude Code, Codex, Codebuddy, Trae, Gemini, and local terminals, LoopDesk is a desktop-first personal loop workspace that unifies context, memory, session state, and loop control across tools. Unlike Orca, it does not become another heavy agent IDE. Unlike Happier, it does not prioritize encrypted remote mirroring over durable loop state. Unlike cc-connect, it does not treat IM as the primary product. Unlike Proma, it does not become a desktop Chat/Agent shell for one vendor workflow; it is the durable cross-tool loop continuity layer above those tools.

### 5.3 Competitive Positioning

| Competitor | Strength | Over-reach | Gap we exploit |
| --- | --- | --- | --- |
| Tutti | shared agent workspace, cross-agent handoff | cloud rooms, collaboration breadth | solo local-first minimal loop |
| WeSight | desktop runtime visibility, multi-engine GUI | GUI shell breadth, IM breadth | lightweight context layer |
| Multica | team task management, runtime daemon, autopilot | team governance, issue board, cloud sharing | personal loop state and continuity |
| Happier | cross-device session control, E2EE, multi-provider support | remote-control/bridge-first product | durable loop-state platform with loop engineering |
| cc-connect | channel breadth, zero-public-IP transports, slash commands | IM-first chat bridge | local-first loop execution and durable `LOOP-STATE.json` |
| Orca | parallel worktrees, rich terminal UX, diff/PR/Linear review | IDE-shell-first product | portable cross-tool context handoff and loop engineering |
| Proma | local-first Chat/Agent workbench, workspace Skills/MCP, remote bot bridges | desktop-shell-first Chat/Agent workflow | durable cross-tool loop state and cross-tool continuity |

### 5.4 Strategic Differentiators
- **Desktop-first runtime**: install, host gateway, access files, run agents, and inspect state locally first.
- **Web as distribution and control surface**: use browser-based setup, inspection, approval, and diagnostics without replacing the desktop runtime.
- **IM as continuation surface**: resume or steer an already-approved workspace task from IM, not run full loops inside chat.
- **Context continuity first**: workspace state is the product, not the shell.
- **Tool-agnostic loop**: MCP-first integration, ACP-second integration, no forced vendor UI.
- **Loop engineering discipline**: triage, maker/checker, run log, budget, escalation, and stop condition as first-class behavior.
- **Local control and portability**: local-first runtime, inspectable state files, export/import, no mandatory cloud account.

## 6. User Experience

### 6.1 Primary Flow
1. Developer installs the LoopDesk desktop app or package for macOS, Windows, or Linux.
2. Desktop app initializes a local loop workspace with `LOOP-STATE.json`, memory, skills, artifacts, and worktree support.
3. Developer connects one or more tools through MCP-first, ACP-second, or tool-specific adapters from the desktop runtime or local web surface.
4. LoopDesk decides whether current work should continue as discovery, triage, synthesis, or bounded Goal execution.
5. Developer inspects state from desktop app or local web UI; sensitive actions require explicit approval.
6. When away from desk, developer opens the web or IM surface to choose a workspace, view status, approve/reject actions, or send follow-ups to an approved in-flight task.
7. Verified results, decisions, and run history are written back to the local workspace.
8. Developer resumes in another tool from durable workspace state instead of re-pasting context.

### 6.2 Desktop-First Principles
- The desktop app owns gateway lifecycle, local file access, agent process management, and worktree isolation.
- The desktop app is the richest inspection surface: run log, diff review, terminal view, approval queue, cost, memory, skills, and artifacts.
- Web surfaces are functional continuations of the desktop workspace, not standalone replicas of full local runtime behavior.
- IM surfaces are intentionally minimal: choose workspace, inspect status, continue approved work, approve/reject, receive compact notifications.

### 6.3 Web Surface Principles
- Web is the preferred onboarding and distribution path for install, guided setup, and first-run configuration.
- Web inspection should show current loop state, active runs, pending approvals, recent artifacts, and channel status.
- Web control should support bounded safe actions: resume read-only inspection, continue approved bounded work, submit approval decisions, view run log, export workspace state.
- Web should never become an excuse to reimplement full local file editing or terminal orchestration at the expense of desktop runtime fidelity.

### 6.4 IM Remote-Control Principles
- IM is optional and disabled by default.
- IM commands map to existing safe workspace actions; no new shell, team-room, or chat-first workflow semantics are introduced.
- The first IM action is usually workspace selection or status inspection, not unbounded execution.
- Long-running or high-risk work remains desktop-owned; IM is for continuation, notification, and lightweight steering.
- When IM cannot carry artifacts or long explanations, the web or desktop surface is the recovery path.

### 6.5 Backend Boundary: Loop vs Goal
- **Loop**: continuously discovers work, triages priorities, maintains a continuous view, and decides whether work should remain exploratory, wait for a human decision, or become a bounded Goal.
- **Goal**: executes a bounded, verifiable task with maker/checker split, approvals, budget caps, and explicit stop conditions; results are written back to the workspace.
- **Frontend boundary**: developer sees one continuous workflow across desktop, web, and IM surfaces; the backend Loop/Goal boundary should not force users to manage separate product modes.
- **Human介入点**: pause only for approval, escalation, ambiguity, high-risk action, or insufficient authorization.

## 7. Desktop-First Scenarios

### 7.1 Install and Initialize Desktop Runtime
- Developer downloads LoopDesk for macOS, Windows, or Linux.
- Desktop app initializes the local gateway, workspace directory, and `LOOP-STATE.json`.
- Developer configures providers, MCP/ACP adapters, and first project from the desktop app or bundled local web setup surface.

### 7.2 Desktop Runtime as Primary Control Surface
- Developer runs a loop workspace from the desktop app.
- Desktop app exposes loop state, run log, memory, skills, artifacts, approvals, cost, and diagnostics.
- Developer switches between coding agents using shared workspace state instead of manual context copying.

### 7.3 Web Distribution and Guided Setup
- Developer opens the product web page to download, verify install requirements, and review setup guidance.
- First-run web surface guides provider auth, adapter selection, workspace template choice, and safety defaults.
- After setup, web becomes an inspection and approval companion, not the main execution runtime.

### 7.4 Web Inspection and Operator Control
- Developer opens the local web UI to inspect active runs, approvals, and cost while the desktop app remains the runtime host.
- Operator can review run log detail, replay packs, channel status, and memory updates from the browser.
- Sensitive actions remain approval-gated and recorded in local workspace state.

### 7.5 Remote Continuation from Web
- Developer is away from the primary desktop but needs to continue an approved bounded task.
- Web surface shows the current workspace, selected in-flight Goal, recent artifacts, and next safe actions.
- Developer can send follow-up guidance, approve a next step, or reject a risky branch; execution remains local when resumed.

### 7.6 IM Workspace Selection and Status
- Developer opens an approved IM channel and selects a LoopDesk workspace.
- IM surface shows current loop status, pending approvals, cost alerts, and a short run summary.
- Developer sees whether the local desktop runtime is active, idle, or waiting for input.

### 7.7 IM Remote Approval and Follow-Up
- LoopDesk sends a compact approval request or cost alert to IM.
- Developer approves or rejects from IM; the result is recorded in the local run log and approval history.
- Developer sends a short follow-up for an in-flight approved task; desktop runtime processes it when active or queues it for the next safe execution window.

### 7.8 Cross-Tool Continuity with Desktop as Source of Truth
- Developer starts work in Claude Code, continues in Codex or Trae, and inspects state in desktop app or web UI.
- Context handoff is driven by `LOOP-STATE.json`, memory, skills, and artifacts.
- IM is used only for lightweight continuation; the authoritative state always remains in the local workspace.

## 8. Scope

### 8.1 In Scope
- Desktop-first local runtime with gateway, workspace state, loop engine, adapters, memory, skills, artifacts, and worktree isolation.
- Desktop app or packaged runtime for macOS, Windows, and Linux.
- Web surfaces for guided setup, workspace inspection, approval decisions, diagnostics, replay, and distribution.
- Optional IM adapters for DingTalk, Feishu/Lark, Slack, and WeCom as lightweight remote control and notification surfaces.
- Normalized IM command surface mapped to existing safe workspace actions.
- Local-first data ownership with export/import, backup, and audit trails.
- v0.1 and v0.2 behavior preserved as the stable baseline for desktop runtime and optional channel adapter behavior.

### 8.2 Out of Scope
- Multi-user collaboration, shared cloud rooms, team workspaces, roles, and enterprise onboarding as core requirements.
- Heavy desktop GUI IDE shell as the primary product differentiator.
- IM-first narrative, rich media pipelines, voice replies, complex card interactions, or chat-first loop execution.
- Mandatory cloud sync, cloud hosting of workspace state, or SaaS accounts for core workflow.
- Personal WeChat, QQ, Telegram, Discord, Matrix, and additional platforms beyond the v0.2 approved adapter set.

## 9. Requirements

### 9.1 Desktop Runtime
- The desktop runtime MUST initialize and manage the local gateway and workspace directory.
- The desktop runtime MUST expose loop state, run log, approvals, memory, skills, artifacts, cost, and diagnostics.
- The desktop runtime MUST support local file access, worktree creation, agent lifecycle management, and runtime restart/recovery.
- The desktop runtime MUST support offline core workflow except for optional IM transports and provider API access.

### 9.2 Workspace State Protocol
- The system MUST maintain `LOOP-STATE.json` as the portable source of truth for tasks, status, results, timestamps, and override history.
- The system MUST keep memory, skills, artifacts, and worktrees inside the same workspace boundary.
- The system MUST support export and import of workspace context without forcing a cloud account.

### 9.3 Cross-Tool Integration
- The system MUST support MCP-first integration for tools, resources, prompts, and tool results.
- The system SHOULD support ACP integration for session lifecycle, streaming updates, and permission flows.
- The system MUST translate inbound tool events into workspace state.
- The system MUST translate workspace state into tool-ready input.
- Tool adapters MUST remain interchangeable; the developer is not forced into one agent shell.

### 9.4 Loop Engine
- The system MUST support scheduled, fire-immediate, durable, and controllable loops.
- The system MUST implement triage, maker, checker, and escalation steps.
- The system MUST record run logs with started, found, acted, escalated, and cost data.
- The system MUST enforce stop conditions and completion criteria.
- Desktop, web, and IM surfaces MUST reflect the same backend loop/goal state.

### 9.5 Memory and Session Continuity
- The system MUST provide durable personal memory with local search.
- The system MUST support long-session compaction and cache continuity.
- The system MUST support session resume, history, export, replay, and abort.
- The system MUST support flushing completed session knowledge into memory.

### 9.6 Skills
- The system MUST support reusable skills and meta-skills inside the personal workspace.
- The system MUST allow inspection, replay, and audit of skill-driven workflows.
- The system SHOULD support skill auto-triggering based on task context.
- Skills SHOULD be organizable per workspace, but MUST remain bound to loop context, memory, artifacts, and approval policy rather than acting as isolated desktop chatbot prompts.

### 9.7 MCP and Extensibility
- The system MUST support stdio and HTTP MCP servers.
- The system SHOULD support per-workspace MCP configuration with enable/disable lifecycle.
- MCP tool results MUST be traceable to workspace, Goal, run, approval, and budget context.
- MCP SHOULD enhance loop continuity, not only chat enhancement inside a single desktop client.

### 9.8 Runtime Visibility and Control
- The system MUST provide desktop-native inspection for active runs, approvals, logs, errors, memory, skills, and worktrees.
- The system MUST provide local web UI for guided setup, runtime inspection, approval decisions, and diagnostics.
- The web surface MUST remain secondary to the desktop runtime and MUST NOT duplicate full local filesystem or terminal semantics as a replacement.

### 9.9 IM Remote Control
- IM adapters MUST be disabled by default and explicitly enabled by the operator.
- IM MUST expose read-only inspection by default and only allow write actions after explicit enablement, allowlisting, and approval-gating.
- IM MUST support workspace selection, status inspection, compact run summaries, approval/reject commands, and bounded follow-up for approved work.
- IM MUST NOT introduce team-room semantics, chat-first loop execution, or unbounded shell access.
- Channel failure, disabled adapters, or unreachable desktop runtime MUST NOT corrupt local workspace state.

### 9.10 Remote Bot Direction
- The system MAY support approved IM bot/transport surfaces for lightweight remote control.
- Remote bot behavior MUST remain bounded: compact commands, status, approval, and bounded follow-up only.
- Transport details MUST stay inside adapters; externally exposed behavior MUST map to existing safe workspace actions.
- Adding a new platform SHOULD first evaluate bounded approval/continuation fit, not rich interaction breadth.

### 9.11 Safety and Cost
- The system MUST track token and cost usage.
- The system MUST enforce budget caps, daily limits, max iterations, and kill switches.
- The system MUST provide an approval queue for sensitive actions.
- The system MUST support escalation for ambiguity, repeated failure, and denylisted paths.
- Desktop, web, and IM approval actions MUST be recorded in the same local audit trail.

### 9.12 Isolation
- The system MUST support per-loop worktree or scratch directory execution.
- The system MUST support cleanup or retained audit snapshots.
- The system MUST avoid cross-loop workspace corruption.
- Remote surfaces MUST not bypass worktree isolation or local safety controls.

### 9.13 Distribution and Deployment
- The system MUST support desktop installers or packages for macOS, Windows, and Linux.
- The system MUST provide web-guided install, setup, and operator documentation.
- The system MUST preserve local workspace data during upgrades and rollbacks.
- The system MUST support local gateway binding to `127.0.0.1` by default and require explicit opt-in for broader exposure with additional auth and network controls.

## 10. Desktop App Surface

### 10.1 Primary Desktop Responsibilities
- Host local gateway and runtime processes.
- Manage workspace files, `LOOP-STATE.json`, worktrees, artifacts, and memory.
- Launch and supervise coding agents with provider credentials stored locally.
- Provide the richest inspection surface for loop/goal state, run log, approvals, cost, skills, and diagnostics.
- Manage local channel adapter status and operator controls.

### 10.2 Desktop User Interface Areas
- Workspace: current loop, active Goal, pending decisions, and next suggested action.
- Agents: configured providers, adapters, runtime status, account/usage view, and rate-limit awareness.
- Run log: started, acted, escalated, approved, rejected, cost, and outcome history.
- Approvals: sensitive action queue with approve/reject/snooze actions.
- Memory and skills: browse, inspect, replay, and mount reusable workflow knowledge.
- Artifacts: generated reports, code, media, exports, and replay packs.
- Worktrees: active isolation contexts, branch/commit context, cleanup candidates, and audit snapshots.
- Channels: adapter status, transport state, restart attempts, enable/disable controls, and compact logs.
- Settings: gateway, provider, adapter, budget, safety, network, and update preferences.

### 10.3 Desktop Runtime Behaviors
- Start default gateway on local loopback with safe defaults.
- Auto-recover from transient runtime or adapter failures without losing workspace state.
- Preserve terminal/session fidelity when launching local coding CLIs.
- Notify desktop user of approvals, budget alerts, and completion events even when web or IM surfaces are also active.

## 11. Web Surface Specification

### 11.1 Distribution Role
- Web is the public entry point for download, release notes, platform requirements, setup guidance, and operator documentation.
- Web should communicate desktop-first positioning clearly: install the desktop runtime for full local fidelity; use web for setup, inspection, and lightweight continuation.

### 11.2 Guided Setup Role
- Web setup should guide provider auth, workspace template selection, MCP/ACP adapter onboarding, channel enablement, and safety defaults.
- Web setup should generate or verify local workspace initialization without replacing desktop runtime authority.
- Web setup should remain workspace-first: every configured action must map to a safe local workspace behavior.

### 11.3 Inspection and Control Role
- Web inspection should show workspace state, active runs, approvals queue, recent artifacts, memory highlights, skills, and channel status.
- Web control should support read-only inspection by default, with explicit operator enablement for approval actions and bounded continuation commands.
- Web should never expose unbounded shell, raw local filesystem editing, or team-room semantics.

### 11.4 Web Recovery Path
- When desktop runtime is unavailable, web should show current known state from local workspace export/sync cache if available.
- When IM delivery is insufficient for artifacts or long explanations, web should serve as the richer recovery surface.
- Web should degrade gracefully: show status, pending actions, and reconnect guidance instead of failing silently.

## 12. IM Remote-Control Specification

### 12.1 Supported Scope for v0.2
- Approved platforms: Slack Socket Mode, Feishu/Lark WebSocket/long-connection, DingTalk Stream, WeCom webhook with explicit public-URL review gate.
- Read commands: `/help`, `/status`, `/current`, `/list`, `/history`, `/memory`, `/skills`, `/model`, `/abort`.
- Write commands: `/new`, `/approve`, `/reject`, `/cancel`.
- Compact notifications: completion, escalation, cost alert, approval request, attention hint.

### 12.2 IM UX Boundaries
- The first IM action is choosing or inspecting a workspace, not running an unbounded loop in chat.
- IM replies are compact and plain-text friendly; long content is summarized with a pointer to desktop or web.
- IM does not replace desktop/web artifact review; large artifacts, diffs, and replay packs stay in desktop/web.
- IM commands are aliases for existing workspace actions; adapter internals stay implementation-specific.

### 12.3 IM Safety Model
- IM adapters remain disabled by default after install or upgrade.
- Unknown senders are treated as viewers or denied write commands outright.
- Write commands require admin allowlist, budget/kill-switch checks, approval flow, and audit logging.
- Channel failure must not corrupt `LOOP-STATE.json`, memory, skills, artifacts, or worktrees.
- Disabling any adapter must preserve all local workspace data and local runtime behavior.

## 13. Skills, MCP, and Remote Bot Design

### 13.1 Workspace-Scoped Skills and MCP
- Each workspace can define its own reusable skills and MCP server configuration.
- Workspace-level MCP config should be the default organization method, not a single global override.
- Skills and MCP should be inspectable, replayable, auditable, and toggleable per workspace.
- Skills should bind to loop context, memory, artifacts, and approval policy, not only isolated chat prompts.

### 13.2 MCP and Loop Engine Integration
- MCP server lifecycle should be managed per workspace: enable, disable, failure recovery, and audit logging.
- MCP tool results should be traceable across workspace, Goal, run, approval, and budget dimensions.
- MCP should enhance cross-tool continuity, not only enhance a single desktop agent runtime.

### 13.3 Remote Bot as Lightweight Controller
- IM/bot behavior should remain bounded: compact commands, status, approval, and bounded follow-up only.
- Approved platforms should be added based on bounded continuation fit, not rich card breadth.
- Transport details should stay inside adapters; externally exposed behavior should map to existing safe workspace actions.

### 13.4 Chat/Agent Layering
- Do not copy Proma's Chat/Agent shell literally into LoopDesk.
- Use the layering insight to separate lightweight inspection from bounded execution and risky automation.
- Simple reads and status checks should stay lightweight; complex bounded work should return to local runtime.

### 13.5 Local Data Inspectability
- Workspace state, session exports, skills, artifacts, and replay packs should remain human-readable and diff-friendly.
- Support partial export: one Goal, one workspace, or one time range at a time.
- Preserve backup, migration, and debugging affordances without forcing cloud sync.

## 14. User Interface Principles

### 14.1 Unified State Across Surfaces
- Desktop, web, and IM must show the same authoritative workspace state.
- State conflicts are resolved by the local workspace, not by chat history or last-write wins in IM.
- Every surface should make clear where the durable source of truth lives: the local workspace.

### 14.2 Desktop-First Fidelity
- Desktop remains the highest-fidelity surface for editing, review, runtime control, and long debugging sessions.
- Web and IM are continuation and control surfaces, not reduced-fidelity replacements for desktop behavior.

### 14.3 Continuity Over Rebirth
- Switching from desktop to web to IM should feel like changing vantage points on the same task.
- The developer should never need to re-paste project rules, recent decisions, or current Goal criteria when moving between approved surfaces.

### 14.4 Action Economy
- Every remote surface action should produce one clear outcome: inspect, continue, approve, reject, or notify.
- Avoid duplicated workflows across desktop, web, and IM; keep one canonical command model and three surface renderings.

## 15. Distribution and Deployment

### 15.1 Desktop Distribution
- Primary install path is a desktop package for macOS, Windows, and Linux.
- Secondary install path is web-guided setup for local gateway and workspace initialization.
- The product must communicate clearly that full fidelity requires the local desktop runtime.

### 15.2 Web Distribution
- Public web presence supports download, setup guidance, docs, release notes, changelog, and operator guidance.
- Web may host lightweight operator/account utilities, but cloud-hosted execution is not the default narrative.
- Web pages must not imply mandatory cloud accounts, team rooms, or SaaS runtime for core workflow.

### 15.3 Local Gateway Exposure
- Default gateway binding remains `127.0.0.1` for safety.
- Public exposure requires explicit operator opt-in, authentication, network controls, and documented risk acceptance.
- IM webhook channels require explicit review gate and documented tunnel, secret rotation, and exposure risk before enabling public callbacks.

## 16. Success Metrics

- Context re-entry time: reduced time re-explaining context when switching tools or surfaces.
- Loop completion rate: share of loops and Goals that reach defined stop conditions.
- Cross-tool fidelity: percentage of handoffs preserving task state, decisions, and artifacts.
- Surface adoption: share of approved work continued from desktop, web, and IM without data loss.
- Cost predictability: share of loop runs within budget and escalation thresholds.
- Remote approval latency: time from IM approval request to recorded decision in local run log.
- Recovery success: share of interrupted sessions resumed from desktop, web, or IM without state corruption.

## 17. Launch Criteria

### 17.1 Desktop-First Launch
- Desktop runtime installs and initializes workspace, gateway, and local web control surface.
- `LOOP-STATE.json`, memory, skills, artifacts, and worktree isolation are functional and inspectable.
- At least one local coding workflow is integrated via MCP or ACP and recorded in workspace state.
- Loop engine supports triage, maker/checker, run log, approvals, budget controls, and stop conditions.
- Local web UI supports guided setup, inspection, approvals, diagnostics, and export.
- Documentation covers install, connect tools, inspect state, run loops, recover from failures, and boundary limitations.

### 17.2 Web Launch
- Public web presence supports download, setup guidance, and operator docs.
- Local web UI remains functional without cloud account and stays workspace-first.
- Web setup and inspection do not expose team-room, cloud-sync, or IM-first narratives as defaults.

### 17.3 IM Launch
- IM adapters remain disabled by default and can be enabled without deleting local workspace data.
- Approved read commands work for workspace selection, status, memory, skills, and history.
- Approved write commands work for `/new`, `/approve`, `/reject`, `/cancel` with audit logging.
- Budget-cap exceeded, escalation, and approval events generate compact notifications without sending large artifacts or raw dumps in v0.2.
- Disabling any adapter preserves local loop workspace behavior.

### 17.4 Quality and Safety
- Focused functional gate passes for loop workspace, CLI, gateway, web UI static views, and channel adapter core behavior.
- No public docs, web UI, or IM narrative leaks team collaboration, cloud-first sync, or channel-first messaging as the primary product.
- Operator can disable channel adapters and retain full local loop workspace functionality.

## 18. Roadmap Alignment

### v0.1 Baseline
- Local-first personal loop workspace with `LOOP-STATE.json`, MCP-first integration, ACP-second integration, loop engine, memory, skills, artifacts, cost/safety controls, worktree isolation, CLI, and local web UI.
- Desktop-first local runtime behavior is the stable foundation for all later surfaces.

### v0.2 Baseline
- Optional IM channel adapters for DingTalk, Feishu/Lark, Slack, and WeCom remain secondary to local workspace.
- Web inspection surface expands to channel status, approval actions, and operator setup.
- IM becomes a continuation and notification surface only; no chat-first loop execution.

### v1.0 Direction
- Desktop runtime packaging improvements, richer desktop inspection, and safer remote continuation.
- Web-assisted guided setup, operator onboarding, and multi-surface approval flows.
- IM remote continuation expands for approved bounded Goals, with continued workspace-first boundaries.
- Incorporate Proma-inspired Skills/MCP/remote bot signals while preserving LoopDesk's durable cross-tool loop state and loop engineering guardrails.

## 19. Risks and Mitigations

| Risk | Mitigation |
| --- | --- | 
| Users treat web or IM as the primary runtime | Keep desktop-first narrative, local gateway authority, and state ownership; web/IM remain secondary surfaces |
| Desktop packaging delays perception of web parity | Use web for guided setup and inspection; do not promise full parity or cloud-first execution |
| IM expands beyond approved safe commands | Disable-by-default adapters, allowlist, budget/kill-switch checks, audit logging, and no unbounded shell semantics |
| Cross-surface state drift | Single local source of truth in `LOOP-STATE.json`; all surfaces read from or write back to workspace state |
| Remote continuation causes unsafe execution | Only approved bounded work may continue remotely; high-risk actions stay approval-gated and desktop-oriented |
| Documentation narrative drift | This PRD is the authoritative source for desktop-first, web-secondary, IM-continuation boundaries |

## 20. Open Questions

- Should LoopDesk ship an Electron desktop shell or remain a local runtime with launcher UX in v1.0?
- What is the minimum viable desktop app shell versus packaged runtime with local browser integration?
- Should web support authenticated multi-machine read-only inspection in a future version?
- Which IM platforms beyond the v0.2 approved set deserve priority in later releases?
- What operator controls are required before allowing public webhook channels in more environments?
- Should LoopDesk introduce optional skill/MCP sharing or publishing while preserving personal-first posture?

## 21. Approval

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
| QA | | Pending |
