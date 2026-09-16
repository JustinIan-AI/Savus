# Competitive Intelligence — `OpenBMB/PilotDeck`

> Research date: 2026-07-21
> Sources: public README and package metadata via GitHub API/repo inspection, `pilotdeck.openbmb.cn` docs pages, official documentation under the project's docs site, local repo inspection.
> Audience: product/engineering planning for LoopDesk.

## 1. Research Method

- Read the public README and metadata for `OpenBMB/PilotDeck` via GitHub API and repo inspection.
- Cross-checked official signals from `https://pilotdeck.openbmb.cn` and its published docs pages.
- Marked uncertainties honestly: some desktop/IM/CLI feature boundaries rely on README/docs phrasing rather than confirmed runtime verification; pricing is not publicly shown in the inspected sources.

## 2. `OpenBMB/PilotDeck`

### 2.1 Product Signal
- Positioning: open-source agent operating system centered on the WorkSpace concept, built for productivity rather than single-turn chat.
- Key promise: keep files, memory, and skills isolated per project, while letting multiple projects run in parallel with controllable cost and traceable memory.
- Target user: developers and power users doing long-running, multi-project productivity work.
- Stated fit: general-purpose multi-task scenarios across Web, CLI, and IM-like channels, with native MCP support.

### 2.2 Core Capabilities
- WorkSpace isolation: each project gets its own operating deck with bounded file scope, project memory, and installed skills.
- White-box memory: users can inspect what the agent remembers, edit or delete entries, pin decisions, and avoid global context pollution.
- Smart routing: tasks can be automatically routed across models by difficulty, instead of always using a single flagship model.
- Always-on behavior: the agent can keep working in the background, discover follow-up work, report progress, and land results as files on disk.
- MCP-native extensibility: MCP servers, tools, skills, lifecycle hooks, and custom memory providers are part of the extension model.
- Multi-surface delivery: README and docs describe Web, CLI, and IM-style surfaces, with onboarding/settings accessible from the UI.
- Installation paths: README shows one-line install, source install, and Docker Compose paths.

### 2.3 Architecture Signal
- Core is modular and layered: Gateway, SessionRouter, AgentSession, TurnRunner, AgentLoop, Context, Router, Model, Tool, Permission, Cron, CLI, Web, and MCP modules.
- Front-end surfaces are described as Web UI, CLI/TUI, Desktop Electron, and Feishu-style channel.
- Local state and memory are persistent; transcripts and memory are stored under a PilotHome-style directory layout.
- Agent runtime is a request/turn pipeline: prepare context, route model, execute request, run tools, stream response back through the gateway/channel.
- Extension layer separates open-source core from plugin customization.

### 2.4 Tech/Platform Signal
- Public repo: `https://github.com/OpenBMB/PilotDeck`
- Homepage: `https://pilotdeck.openbmb.cn`
- License: AGPL 3.0
- Language: TypeScript
- Docs site technology: Docusaurus-based published docs
- Install/runtime signals from README: Node.js, pnpm, optional Docker, local config under `~/.pilotdeck/pilotdeck.yaml`
- Open-source launch signal: announced as open source on 2026-05-28
- Release signals observed: desktop releases such as `v260623` and `v0.1.0`
- Repo signals as of research: `3,860` stars, `408` forks, `118` open issues
- Last repo push during research: `2026-07-20`

### 2.5 Uncertainties
- Exact IM/Feishu feature depth is described in README/docs language, but runtime verification was not completed in this research pass.
- Pricing and commercial edition boundaries are not clearly shown in the inspected public sources.
- Desktop and Web UI feature parity, offline behavior, and exact permission model are best treated as public-signal only until confirmed from runtime docs or release notes.

## 3. Relevance to LoopDesk

### 3.1 Why PilotDeck matters for LoopDesk planning
- It validates that users care about project-level isolation, inspectable memory, and cost-aware multi-agent productivity.
- It reinforces that local-first state and skill reuse are becoming baseline expectations, not nice-to-haves.
- It is a useful adjacent reference for structured task memory, routing, background execution, and extension protocols.

### 3.2 Contrast with LoopDesk
| Dimension | `OpenBMB/PilotDeck` | LoopDesk |
| --- | --- | --- |
| Primary abstraction | WorkSpace as an agent operating deck | durable `LOOP-STATE.json` and loop continuity |
| Memory model | white-box, editable, workspace-scoped memory | durable cross-tool memory/skills/artifacts with adapter-first handoff |
| Cost control | smart routing and per-task cost awareness | cost observability, approvals, budget caps, run logs |
| Multi-surface | Web / CLI / IM / Desktop | lightweight CLI + local Web UI first |
| Orchestration focus | Always-on background productivity, routing, MCP-native extensions | Loop Engineering: triage, maker/checker, escalation, stop condition |
| Git/workflow | worktree detection inside a broader deck model | worktree isolation is present but secondary to portable loop state |
| Open-source framing | community-oriented agent OS | local-first personal loop workspace for independent developers |
| Commercial posture | no clear verified pricing model in inspected sources | current docs center open local-first workflow rather than SaaS packaging |

### 3.3 What LoopDesk should borrow
- WorkSpace-style isolation when reasoning about per-project memory and skill boundaries.
- White-box memory as a design direction: users want inspectable and editable context, not opaque black-box chats.
- Smart routing as a reference pattern for cost-aware model selection across routine and hard tasks.
- MCP-native extensibility as a first-class integration strategy.

### 3.4 What LoopDesk should not copy
- Building another heavy multi-surface agent OS unless LoopDesk explicitly wants to compete on platform breadth.
- Treating one workspace app as the only durable source of truth for cross-tool loops.
- Assuming desktop/IM fidelity is more important than portable loop state and cross-CLI continuity.

## 4. Recommendations

- Treat PilotDeck as a strong reference for WorkSpace isolation, inspectable memory, routing-aware cost control, and MCP-native extension design.
- Do not treat PilotDeck as the product model for LoopDesk because its center of gravity is an agent operating system, not portable loop continuity across Claude Code, Codex, Codebuddy, Trae, and Gemini.
- Recommended LoopDesk focus areas against PilotDeck:
  - durable `LOOP-STATE.json` as the portable source of truth across tools
  - explicit adapter layer for coding CLIs, MCP/ACP, and optional lightweight surfaces
  - Loop Engineering discipline: triage, maker/checker, escalation, run log, stop condition
  - local-first memory/skills/artifacts with optional cross-tool handoff
- Recommended monitoring topics:
  - whether PilotDek matures from a promising open-source platform into stable desktop/IM/CLI parity
  - whether its WorkSpace model ever exports durable cross-tool state beyond its own runtime
  - whether commercial boundaries, telemetry, or hosting assumptions shift its local-first posture

## 5. Open Questions
- Confirm exact IM/Feishu feature boundaries and whether the channel support is production-ready or still exploratory.
- Confirm pricing, commercial support, and any enterprise/cloud components beyond the open-source core.
- Confirm how PilotDeck's WorkSpace memory and session files behave under git worktrees, concurrent projects, and cross-machine workflows.
- Confirm whether Smart Routing cost claims are reproducible in independent environments and under which provider configurations.
*** End Patch
PATCH