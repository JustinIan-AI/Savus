# Competitive Intelligence — Orca (`stablyai/orca`)

> Research date: 2026-07-30
> Sources: GitHub MCP `read_mcp_resource` for `README.md`; direct GitHub API/metadata reads for `package.json`, `docs/` tree, `.github/CONTRIBUTING.md`, `src/` tree, plus selected primary doc reads: `docs/readme/README.zh-CN.md`, `docs/reference/headless-linux-server.md`, `docs/reference/remote-agent-session-host-authority.md`, `docs/reference/resource-manager-memory-metrics.md`, `docs/claude-usage-tracking-codexbar-parity.md`, `docs/claude-scoped-oauth-usage-limits.md`, `docs/native-chat-codex-tui-parity.md`, `docs/orchestration-primitives.html`.
> Scope: public repo surface and product docs only; no server-side runtime was cloned.

## 1. Research Method

- Read `stablyai/orca/README.md` with GitHub MCP `read_mcp_resource`; this repo supports the repository-content resource for files, not directories.
- Used direct GitHub API metadata reads for root repo items, `docs/`, `src/`, and `.github/` because repo-content resources reject directory listings.
- Read selected primary docs/source references directly from GitHub content API/base64 decode; no `git clone` was performed.
- Cross-checked findings against LoopDesk product positioning, PRD, architecture, and existing competitive-intel summary.

## 2. Product Identity

### 2.1 Positioning
- **Primary repo label**: `The AI Orchestrator for 100x builders.`
- **Core pitch**: run **Codex, Claude Code, OpenCode, or Pi** side-by-side, each in its own **worktree**, tracked in one place.
- **Platform claim**: available for macOS, Windows, and Linux.
- **Short description from `package.json`**: `Next-gen IDE for parallel agentic development`.
- **Distribution claim**: official `onOrca.dev/download` site, GitHub Releases downloads, Homebrew/AUR packaging, signed Windows builds, and mobile companion apps.

### 2.2 Target User
- Primary: builders who already use coding CLIs and want one local surface for parallel agent work, review, and execution.
- Secondary: developers who want GitHub/Linear-linked workflows, remote SSH execution, browser/UI feedback loops, and mobile monitoring.
- Not primarily positioned for developers whose main need is portable continuation across independent external tools without a branded desktop shell.

### 2.3 Differentiation Claim
- **No-login local mode**: bring your own Claude Code or Codex subscription; no mandatory cloud account to run.
- **Worktree-native execution**: fan prompts across isolated worktrees, compare outputs, and merge the winner.
- **Rich desktop runtime**: terminal splits, diff annotation, embedded browser/Design Mode, GitHub/Linear review.
- **Remote and mobile continuity**: SSH worktrees, host-authority rules for remote sessions, and mobile companion for monitoring/steering.
- **Active packaging**: reproducible builds/scripts, reliability gates, headless Linux server support, and usage/routing parity work.

### 2.4 Important Scope Boundary
- This is the public surface of a desktop product repo; advanced commerce, hosting, or mobile bundling details may be managed outside this repo.
- Some implementation details appear in contributor docs and working notes; treat them as current direction, not frozen API promises.

## 3. Architecture Overview

### 3.1 System Shape
- **Desktop app** built with Electron, Electron Vite, React, TypeScript, and zustand state.
- **CLI surface** exists under `src/cli`; `package.json` exposes `orca` and `orca-dev` binaries.
- **Mobile companion** is mentioned in public README/docs, but this repo's primary work is desktop-first.
- **Headless runtime** is explicitly supported: `docs/reference/headless-linux-server.md` describes `orca serve` on Linux headless boxes, AppImage extraction, Xvfb handling, and foreground/service run modes.
- **Release/support docs** mention Apple Silicon/Intel/Windows/Linux AppImage builds and signed Windows downloads, so this is a packaged distribution product.

### 3.2 Runtime Domains
- `src/main` exposes broad desktop runtime domains: `claude`, `codex`, `gemini`, `cursor`, `cline`, `goose`, `amp`, `augmentcode`, `browser`, `ghostty`, `git`, `github`, `linear`, `daemon`, `cli`, and agent/runtime domains.
- `src/renderer` indicates a rich React renderer surface.
- `src/preload` and `src/shared`/`src/types` provide Electron boundary/type layers.
- Product/runtime governance is visible in docs and scripts rather than a single `AGENTS.md` in this repo read.

### 3.3 Docs and Source Discipline
- `docs/` is a mix of public README translations, product design notes, platform compatibility docs, and runtime reliability references.
- Working docs contain implementation-level rationale with file paths and issue anchors, suggesting active product iteration.
- `docs/native-chat-codex-tui-parity.md` shows Orca is actively improving native-runtime parity instead of leaving all behavior as PTY typing.

## 4. Core Capabilities

### 4.1 Parallel Worktrees
- README feature block: `Fan one prompt across five agents, each in its own isolated git worktree — compare the results and merge the winner.`
- This makes worktree the central execution unit, not a chat transcript.
- Relevant to LoopDesk as validation that developers want **work isolation + winner selection**, but LoopDesk should keep this portable rather than shell-bound.

### 4.2 Multi-Agent Terminal UX
- README highlights `Ghostty-class terminals with WebGL rendering, infinite splits, and scrollback that survives restarts`.
- README/localized docs also highlight active-run notifications, monitoring, and follow-ups from the desktop.
- This proves runtime visibility matters, but LoopDesk can satisfy that with lighter CLI/local Web UI surfaces.

### 4.3 Review and Source Control
- README highlights `Annotate AI Diffs`: comment on AI-generated diffs and ship feedback back to the agent without leaving Orca.
- README also highlights GitHub/Linear-native task browsing and worktree opening from issues/PRs.
- This is strong adjacent inspiration for LoopDesk's review/approval affordances, but LoopDesk should keep it tool-agnostic and portable.

### 4.4 Browser/Design Mode and Structured Context
- README: click a UI element in a real Chromium window and send HTML/CSS/screenshot into the agent prompt.
- This validates that agent workflows increasingly need **observation -> structured context -> revision** loops rather than only text chat.

### 4.5 Remote Execution and Session Host Authority
- `docs/reference/headless-linux-server.md` documents `orca serve`, headless Linux deployment, and self-hosted runtime behavior.
- `docs/reference/remote-agent-session-host-authority.md` defines an implemented single-PR v1 remote-session invariant: canonical PTY ownership, host-decided session identity, stale client rejection, exit retirement, and deterministic repro coverage.
- This is more concrete than generic “SSH support” marketing: it shows Orca is investing in **remote agent session reliability**, not just surface connectivity.

### 4.6 Usage Tracking and Account Switching
- `docs/claude-scoped-oauth-usage-limits.md` documents Claude OAuth `limits` parsing, scoped weekly usage windows, fallback field compatibility, and platform caveats.
- `docs/claude-usage-tracking-codexbar-parity.md` documents usage/limit parity work.
- These imply Orca treats **account/routing/cost observability** as first-class product plumbing.

### 4.7 Native Chat / TUI Parity
- `docs/native-chat-codex-tui-parity.md` explicitly says native chat currently types into Codex TUI via PTY, which means it does not fully own model/reasoning/permissions/session lifecycle yet.
- This is important because it contradicts any assumption that Orca already exposes deep external agent protocol ownership; it is still working toward cleaner native parity.

### 4.8 Skill/CLI Extension Path
- README references `npx skills add https://github.com/stablyai/orca --skill orca-cli`, implying a CLI-led skill-install/distribution model.
- This signals portability interest, but the primary value stays inside Orca's desktop/runtime ecosystem.

## 5. Competitive Comparison with LoopDesk

| Dimension | `stablyai/orca` | LoopDesk |
| --- | --- | --- |
| Primary metaphor | next-gen IDE for parallel agentic development | personal loop workspace / control plane |
| Core unit | worktree + terminal pane + review surface | `LOOP-STATE.json`, memory, skills, artifacts |
| Target user | local builders orchestrating coding CLIs | independent developers continuing work across Claude Code / Codex / Trae / Gemini |
| Local-first | local desktop + mobile companion + headless serve | local-first workspace files + portable cross-tool handoff |
| UX surface | Electron desktop, terminal splits, browser/design mode, mobile companion | lightweight CLI + local Web UI |
| Worktree model | first-class parallel worktrees, winner selection, issue-linked worktrees | per-loop safe automation isolation/worktree support |
| Cross-tool continuity | strong inside Orca runtime/CLI ecosystem; less clear as external portable handoff | durable portable loop state across external tools |
| Review / approval | annotate AI diff, GitHub/Linear review, commit flow | explicit approvals, maker/checker, run log, escalation |
| Mobile/channel | first-class mobile companion app | IM/mobile deferred from v0.1/v0.2 |
| Extension surface | broad CLI agent support + skill install + native chat parity work | MCP-first adapter layer + ACP-second adapters |

## 6. Competitive Analysis

### 6.1 Direct relevance to personal-loop workspace
- Orca validates **parallel worktree execution** instead of serial chat reruns.
- Orca validates **structured review** on agent output before finalizing changes.
- Orca validates that developers want **remote/hosted session authority**, not just local-binary convenience.
- Orca remains a different product category: it is a **desktop IDE/runtime**, while LoopDesk is the **portable state + control layer underneath multiple shells**.

### 6.2 Strategic differentiation
- LoopDesk should win by keeping work portable, inspectable, and tool-agnostic with durable `LOOP-STATE.json`, cross-tool memory, skills, and loop engineering discipline.
- Orca wins when the user chooses to become an Orca user; LoopDesk wins when the user wants to continue the same work in Claude Code, Codex, Trae, or Gemini without adopting a new shell.
- LoopDesk should borrow:
  - per-loop worktree isolation semantics
  - lightweight approval/diff UX
  - remote host-authority/state thinking without requiring Orca’s desktop runtime
  - usage/cost transparency as user-facing product behavior
- LoopDesk should avoid cloning:
  - heavy Electron IDE shell
  - native IDE marketing and packaging overhead
  - app-branded desktop/mobile-first narrative

### 6.3 Gaps vs our direction
- Orca is too **desktop-IDE-first** for LoopDesk's lightweight portability promise.
- Orca's continuity advantage largely stays inside Orca; there is no clear evidence yet of durable external `LOOP-STATE.json`-style exports to arbitrary external tools.
- Orca's mobile/design/browser/terminal breadth exceeds LoopDesk's v0.1/v0.2 minimal surface.
- Native chat parity docs show Orca is still sanding down external-agent boundaries; LoopDesk can expose cleaner cross-tool adapters earlier.

## 7. Recommendations

- Treat `stablyai/orca` as the primary reference for **worktree-native agent execution, terminal/run visibility, diff/approval UX, headless/remote session authority, usage/routing observability, and desktop packaging expectations**.
- Do not treat it as the product model for LoopDesk.
- Recommended LoopDesk focus:
  - durable `LOOP-STATE.json` and cross-tool adapter-first continuity
  - explicit per-loop worktree isolation and lightweight review/approval UX
  - local CLI + local Web UI instead of Electron desktop-first shell
  - cost/account observability without requiring a branded login wall
- Recommended guardrail:
  - avoid desktop IDE shell, design-mode browser, heavy Electron app maintenance, and mobile-first narrative in v0.1/v0.2 unless explicitly prioritized later

## 8. Open Questions

- Confirm whether Orca supports durable export/import of loop/worktree state to external coding agents, or whether continuity remains internal to its own runtime.
- Confirm whether any strong orchestration/desktop features in this repo remain desktop-only and are not surfaced through reusable local protocols.
- Confirm whether the open `stablyai/orca` repo contains the full commercial/runtime surface or whether some distributions remain gated from OSS inspection.
- Confirm whether Orca plans durable cross-tool handoff beyond its own worktrees/tabs/channels.
- Confirm whether the CLI/skill path is intended as a portable protocol or remains desktop-app bound.
- Confirm pricing, privacy, and telemetry boundaries among open-source usage, official `onOrca.dev` distribution, and any cloud/hosted modes.
