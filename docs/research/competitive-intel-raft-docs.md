# Competitive Intelligence — Raft Docs (`docs.raft.build`)

> Research date: 2026-07-22
> Sources: `https://docs.raft.build/welcome/` public docs page, VitePress-rendered page signals, `https://github.com/botiverse/raft-docs` README/docs repo signals, local repo inspection.
> Audience: product/engineering planning for LoopDesk.

## 1. Research Method

- Read the public welcome page at `https://docs.raft.build/welcome/` and extracted visible page text, nav structure, and section labels.
- Cross-checked the public docs repository `botiverse/raft-docs` for stack, content structure, and LLM-friendly delivery format.
- Marked uncertainties honestly: deeper feature behavior, pricing, and production-readiness claims rely on public docs signals rather than verified runtime deployment.

## 2. Raft Docs

### 2.1 Product Signal
- Positioning: documentation and onboarding surface for **Raft**, described as a workspace where humans and AI agents work together.
- Key promise: agents are treated as persistent teammates with identities, memory, and collaboration ability; humans set direction and steer.
- Target user: teams and builders adopting Raft as a shared agent workspace, not specifically solo developers.
- Stated fit: first-run onboarding, task handoff, teammate collaboration, agent team building, cross-device access, and tutorial-led adoption.

### 2.2 Core Capabilities
- Onboarding agent: guided first-run experience to create a server, connect a computer, and meet an initial agent.
- Task handoff: users can give agents real work and track returned results.
- Teammate collaboration: humans and agents share a room-like workspace with conversation and direction setting.
- Agent team building: add multiple agents, shape roles, and grow a team that learns over time.
- Work visibility: catch-up surfaces, search, and notifications for important activity.
- Cross-device access: mobile-friendly access so the team is available from phones.
- Developer integration: documented Login with Raft integration path for external apps.
- LLM-friendly docs: public docs expose structured TOC and Markdown source for AI consumption.

### 2.3 Architecture Signal
- Docs site is built with **VitePress**, indicating Markdown-first public documentation.
- Content is stored as plain Markdown under a `content/` tree rather than a custom CMS.
- The docs build emits both human HTML pages and agent-readable Markdown files.
- The documentation repo is separate from the main product repo and functions as the public docs source of truth.
- No verified backend architecture, runtime stack, or deployment topology is disclosed in the inspected docs site alone.

### 2.4 Tech/Platform Signal
- Public docs site: `https://docs.raft.build` with `docs.slock.ai` noted as a 301 redirect to the same docs site.
- Docs repo: `https://github.com/botiverse/raft-docs`
- Docs stack: VitePress, TypeScript for config/build helpers, Markdown content.
- Content path pattern: `content/welcome/index.md`, `content/features/...`, `content/developers/...`.
- LLM-friendly endpoints: `/llms.txt` for structured TOC, `/<page>.md` for raw Markdown source.
- Site metadata: title `Raft Docs`, description emphasizes shared channels, threads, and time between humans and agents.
- Last observed docs page update signal: 2026-07-22 on the welcome page.

### 2.5 Packaging and Release Signal
- No verified product release tags, version matrix, or packaging manifests were found in the docs site itself.
- The docs repo is public and open for contribution, but product release cadence must be confirmed from the main Raft repo or product site.
- Mobile access is mentioned as a product behavior, but app packaging details are not disclosed in the inspected docs.

### 2.6 Uncertainties
- Exact product architecture, hosting model, agent runtime, persistence layer, and security boundaries are not fully explained in the inspected docs pages.
- Pricing, commercial tier boundaries, and enterprise controls are not shown in the inspected public docs.
- Feature completeness for agent collaboration, channels, tasks, and files relies on docs copy; runtime verification was not completed.
- The relationship between `docs.raft.build`, `docs.slock.ai`, `raft.build`, and the core product repo should be confirmed if used for integration planning.

## 3. Relevance to LoopDesk

### 3.1 Why Raft docs matter for LoopDesk planning
- It reinforces that users expect agent workspaces to feel like shared rooms with persistent identities, memory, and task continuity.
- It validates that onboarding, task handoff, team visibility, and cross-device access are becoming baseline expectations for agent platforms.
- The Markdown-first, LLM-friendly docs pattern is a useful reference for how agent platforms may publish machine-readable product knowledge.

### 3.2 Contrast with LoopDesk
| Dimension | Raft Docs / Raft | LoopDesk |
| --- | --- | --- |
| Primary metaphor | shared agent room with humans and agents | personal loop workspace with durable `LOOP-STATE.json` |
| Memory/state | persistent agent memory and team context | cross-tool loop state, memory, skills, artifacts |
| Collaboration | multi-human + multi-agent room | solo/independent-developer-first, local-first |
| Surface emphasis | docs-led onboarding, team app, cross-device | CLI + local Web UI, optional IM continuation, future Desktop packaging |
| Loop engineering | not visible in inspected docs | triage, maker/checker, run log, escalation, stop condition |
| Adapter strategy | Login with Raft integration mentioned | explicit MCP-first / ACP-second adapter layer |
| Openness signal | public docs repo, community invite | local-first portable state, inspectable files |
| Commercial posture | unclear from inspected docs | current docs center open local-first workflow |

### 3.3 What LoopDesk should borrow
- Strong onboarding-as-narrative pattern: guide users from first run to first useful task quickly.
- Task handoff mental model: frame agent work as returning completed, reviewable results.
- Team/collaboration language as a reference for later shared-boundary features, while keeping LoopDesk personal-first.
- Markdown-first, machine-readable documentation as a pattern for LoopDesk docs and future agent-readable references.

### 3.4 What LoopDesk should not copy
- Multi-user room or team-first collaboration as the core narrative.
- Heavy app/room abstraction that risks making local loop state secondary.
- Assuming cross-device sync or shared-agent identity should override local-first authority and `LOOP-STATE.json`.

## 4. Recommendations

- Treat Raft as a useful reference for agent-onboarding UX, task handoff framing, and team-collaboration narrative patterns.
- Do not treat Raft as the product model for LoopDesk because its documented center of gravity is a shared human-agent workspace, not portable personal loop continuity across Claude Code, Codex, Codebuddy, Trae, and Gemini.
- Recommended LoopDesk focus areas against Raft:
  - keep `LOOP-STATE.json` as the durable source of truth
  - maintain lightweight CLI + local Web UI as the primary surface
  - preserve cross-tool adapter-first integration instead of forcing one agent room/shell
  - add onboarding and task handoff clarity, but only when it serves local loop engineering
- Recommended monitoring topics:
  - whether Raft publishes clearer runtime architecture, local-first guarantees, and developer integration details
  - whether Raft's agent-room model evolves toward durable cross-tool state export beyond its own platform
  - whether docs.slock.ai remains a docs alias or becomes a separate product surface

## 5. Open Questions
- Confirm the exact relationship between `docs.raft.build`, `docs.slock.ai`, `raft.build`, and the core product repo.
- Confirm whether Raft's agent identity/memory model is local-first or cloud-dependent.
- Confirm pricing, commercial tiers, and enterprise controls if considering integration or competitive positioning.
