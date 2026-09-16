# Competitive Intelligence — Cindy (`makecindy/cindy`)

> Research date: 2026-07-30
> Sources: primary `makecindy/cindy` repo files via GitHub MCP and direct GitHub API metadata reads: `README.md`, `README.zh-CN.md`, `AGENTS.md`, `docs/README.md`, `docs/product-rules/core-product-principles.md`, `docs/product-rules/region-and-editions.md`, `docs/dev-rules/repo-map.md`, `docs/dev-rules/orca-team-architecture.md`, `docs/dev-rules/maker-core-and-agent-behavior.md`, `docs/dev-rules/plugin-security-and-authoring.md`, root `package.json`, repo tree for `apps/`, `packages/`, `docs/`, `config/`, and selected package/service metadata under `apps/desktop/src/main`.

## 1. Research Method

- Read the README in English and Simplified Chinese to understand public positioning, monorepo boundary, supported harnesses, and regional publishing modes.
- Inspected the repo root rule index and authoritative product/engineering docs to verify client-only scope, package boundaries, and governance rules.
- Verified source-level boundaries via `apps/desktop/src/main` tree evidence and `config/endpoint.json`-style configuration ownership; backend runtime was not cloned because this repo explicitly scopes to client/mobile/shared packages.
- Cross-checked findings against LoopDesk product positioning, PRD, and competitive-intel summary.

## 2. Product Identity

### 2.1 Positioning
- Cindy describes itself as an **open-source AI agent that works out of the box**.
- It brings multiple harnesses, models, and tools into one agent that finishes **real work in projects and apps**.
- Key client-side promise: run locally on the developer's machine using real files and logged-in apps.

### 2.2 Target User
- Primary user is a developer or knowledge worker who wants AI help without manually managing CLI keys, agents, and model routing.
- Secondary appeal is cross-device continuity and team reuse via skills and plugins.
- It is not positioned as an enterprise AI platform; it is a **client/workbench** that connects to the Cindy service for richer capabilities.

### 2.3 Differentiation Claim
- **Hosted + skip-sign-in local modes**: users can use official cloud or run local-only agents without signing in.
- **Harness mixing and mid-task switching**: Claude Code, Codex, future native harness, and models can switch while workspace, memory, skills, and tools stay continuous.
- **Multi-agent execution within one product**: one task can be planned, executed in parallel, and reviewed by agents on different harness × model combinations.
- **Rich client surface**: desktop Electron app, Expo mobile app, device-link remote control, IM input, scheduled tasks, browser/computer/phone control, and an open plugin marketplace.
- **Out-of-the-box onboarding**: common connections and authorizations are automated in the product rather than pushed onto the user.

### 2.4 Important Scope Boundary
- This repository is the **open-source client** for Cindy.
- Backend service is in a separate repository and not included here.
- Server-backed capabilities are unavailable when the user selects **Skip Sign-In**.

## 3. Architecture Overview

### 3.1 System Shape
- **pnpm monorepo** with `apps/desktop`, `apps/mobile`, `packages/*`, and `cindy-protocol/` as a git submodule.
- `apps/*-bin` downloads `claude-code`, `codex`, and `ripgrep` binaries during `pnpm install`; Android platform-tools are fetched before Windows packaging.
- The public local-only path uses local agent capabilities, but official download, auto-update, and hosted premium flow come from the official CDN/service unless self-hosted.

### 3.2 Client Packaging
- Desktop client: `apps/desktop` based on Electron + Vite.
- Mobile client: `apps/mobile` based on Expo / React Native; supports same-account login, remote desktop discovery/control, and mirrored sessions.
- `package.json` workspace dependencies expose a broad shared runtime: `maker-core`, `orca-workflow`, `maker-scheduler`, `device-link`, `lizi-im`, `browser-control-runtime`, `project-context`, `auth-client`, `model-providers`, and more.

### 3.3 Runtime Ownership
- `maker-core` is the shared agent/session/event abstraction with **no Electron dependency**.
- `orca-workflow` owns multi-worker orchestration lead-side responsibilities including MCP bridging.
- `maker-scheduler` owns cron scheduling plus storage/runner/notifier interfaces.
- `project-context` is described as the project knowledge layer driven by commits.
- `device-link` owns cross-device remote control with allowlisted IPC topics and topic routing.
- `lizi-im` owns IM transport; `browser-control-runtime` owns browser automation; `github-client`, `gitlab-client`, and `embedding-client` supply first-party service access.
- Desktop source is split into `main` and `renderer` with `preload` and shared types; desktop uses local SQLite/migrations and local DB proxy layers.

### 3.4 Regional Delivery
- Two shipping editions: `global` and `cn`.
- `dev` is an internal build identity, not a user-facing edition.
- Global edition takes the unbranded/default identity; `cn` gets regional branding.
- Region is a build-time dimension, not a user-runtime choice.
- Endpoint manifests are region-specific: `config/endpoint.json`, `config/endpoint.global.json`, and `config/endpoint.dev.json`.

### 3.5 Rules and Governance
- `docs/README.md` marks product, design, and dev rules as `authoritative`.
- Product rules are organized under `docs/product-rules/`; engineering rules under `docs/dev-rules/`.
- `orca-team-architecture.md` is described as the sole authoritative doc for Orca collaboration architecture and execution-unit planning.
- `maker-core-and-agent-behavior.md` governs agent orchestration, prompt assembly, translator behavior, model mapping, cache-rate/performance/accuracy metrics, and system-prompt gating.
- `plugin-security-and-authoring.md` governs plugin sandboxing, permissions, network/credential/resource handoff, author-visible contract sync, and known security gaps.

## 4. Core Capabilities

### 4.1 Harness and Model Connectivity
- Ships with **Claude Code** and **Codex** harness support; native harness is incoming.
- Model and harness mix freely within one task.
- Mid-task harness/model switching is supported while preserving workspace context.
- Users may bring models via official hosted usage, existing paid Coding Plan authorization, custom API keys, or local models.
- Preferred UX: hide key/CLI/MCP/runtime complexity from the user and automate discovery, onboarding, and fallback.

### 4.2 Desktop App Surface
- First-class Windows/macOS Electron desktop client with desktop-first development workflow and packaged release path.
- Desktop docs imply rich panels, login/auth flows, help/knowledge-base generation, OAuth preview, export templates, migration validation, and desktop DB tooling.
- Desktop scripts include workspace/worktree management, Mac window setup, remote/local restart, and dependency assurance.
- Desktop packaging uses `electron-forge`; there are typed DB, migration replay, and DB proxy performance tests.

### 4.3 Mobile App Surface
- Expo/React Native mobile app supports same-account login, remote desktop discovery/control, and mirrored session visibility.
- Mobile has separate release, simulator, build, and release-check flows.
- Mobile is listed as a direct consumer of only five shared packages, indicating a thinner runtime than desktop.

### 4.4 Remote and Multi-Device Continuity
- Desktop can SSH into remote workspaces through `maker-remote-ssh` with `~/.ssh/config`-aware connection pools.
- `maker-cc-manager` provides NDJSON RPC daemon behavior for Claude Agent SDK in remote execution, exposing multi-session and detach/reattach capabilities.
- `device-link` provides cross-device remote control with allowlisted IPC topics and reconnect/heartbeat handling.
- Multi-device behavior aims for consistent task semantics across desktop, mobile, remote control, IM, and scheduled tasks.

### 4.5 Multi-Agent and Orca-Style Teamwork
- One task may be **planned, executed in parallel, and reviewed** by agents on different harness × model combinations.
- `orca-workflow` is treated as lead-side MCP bridging plus orchestration prompts; desktop owns `maker-ipc/orca*` services.
- Team/skill orchestration doc emphasizes deterministic tool/MCP/user reachability, execution ownership validation, and worker lifecycle discipline.
- Orca docs speak of future execution-unit vision, runner layering, side chat, relationship contracts, and nine control-plane mechanisms.

### 4.6 Browser, File, and IM Control
- `browser-control-runtime` wraps playwright-core + MCP-style browser automation.
- `file-browser-core` handles workdir scanning, ignore matching, and ripgrep search; desktop shares this with remote-file-service.
- `lizi-im` supplies IM transport with attachment download, unified send APIs, and host-injected adapters.
- Docs require registration of IPC/push allowlists when new push paths need remote, mobile, or IM behavior.

### 4.7 Scheduling and Automation
- `maker-scheduler` exposes cron-like scheduled tasks with storage/runner/notifier interfaces.
- README frames automation as recurring work that schedules itself, runs itself, and reports back.
- Product rules explicitly treat repeated work as a first-class long-term capability.

### 4.8 Skills, Plugins, and Extensibility
- **Skill**: encodes a work method using natural language, scripts, or tool orchestration; reusable for individuals and teams.
- **Plugin**: sandboxed mini-program that delivers structured, interactive outcomes between agent and user.
- Plugin protocol emphasizes structured data and events; arbitrary LLM text parsing is not the primary protocol.
- Plugins cannot bypass Cindy's permission/safety boundaries; manifest slots, channel security checks, model slot allowlists, and packaging rules are tightly governed.
- Plugins may register panels and theme tokens through a strict whitelist.
- Team sharing of skills and an open plugin marketplace are explicitly noted as **in the making**.

### 4.9 Memory and Workspace Continuity
- README states memory is shared across harnesses and persists corrections/behavior preferences across sessions.
- No explicit repo-local durable workspace-state file like `LOOP-STATE.json` was found; continuity appears service-backed by default.
- Skip-sign-in local mode can use local agents, but docs emphasize server-backed capabilities are unavailable in that state.

### 4.10 Security and Guardrails
- Credentials, authorization files, and secrets are governed by strict desktop/mobile pipelines.
- Plugin runtime rules require process isolation, host-verified identity, network allowlists, no direct Node/host filesystem/network access, and audited media/resource handoff.
- DCO is required for contributions; CLA is not required.
- Analytics exist in official distributions; from-source builds can disable telemetry.

## 5. Competitive Comparison with LoopDesk

| Dimension | Cindy | LoopDesk |
| --- | --- | --- |
| Primary metaphor | desktop/mobile AI agent client/workbench, out-of-the-box assistant | personal loop workspace and control plane |
| Target user | normal users and developers who want one connected AI agent without manual CLI/model maintenance | independent developers managing Claude Code, Codex, Codebuddy, Trae, Gemini, and local loops |
| Core promise | finish real work with harness/model/plugin/multi-device continuity | keep context, memory, and loop state portable across external coding agents |
| Local-first | yes, but hosted/skip-sign-in boundaries favor a service-connected desktop app | yes; core workspace files and loop state are local-first |
| Cross-tool context | strong inside Cindy harness/model continuity, but dependent on client + backend service | strong cross-tool continuity prioritized as portable workspace state |
| Multitasking | first-class parallel planning + execution + review within one task | first-class loop engineering, maker/checker, stop conditions, and run log |
| Desktop/mobile | strongly prioritized with mandated product behavior | Desktop/local Web UI are primary for v0.1-v0.2; mobile is not primary |
| IM/channel | first-class IM and channel intent | bounded adapter surface, not IM-first |
| Plugin marketplace | planned open marketplace plus authored plugin contracts | skills/meta-skills and MCP-first extension, not a broad marketplace-first story |
| Extension model | Skill + plugin with strict security/contracts | skills plus MCP/ACP adapters and durable workspace artifacts |
| Installation cost | higher than a lightweight CLI: Electron + mobile builds + agent binaries + optional cloud account | low; lightweight local-first CLI + local Web UI |
| Operational model | hosted-first client with optional local-only agent mode | local-first loop workspace without mandatory cloud identity |

## 6. Competitive Analysis

### 6.1 Direct relevance to personal-loop workspace
- Cindy validates that users want **out-of-the-box onboarding**, not a setup-heavy local CLI.
- Cindy validates that **device continuity, schedule automation, and structured plugin interactions** are expected from modern agent products.
- Cindy validates that **multiple harnesses in one coherent product** can be a competitive advantage when the product hides routing complexity.
- Cindy remains on the wrong side of LoopDesk's niche because it is a **vanity-UI-first client/workbench** built around its own service curve and product narrative, not a minimal portable loop-state layer.

### 6.2 Strategic differentiation
- LoopDesk should still win by being **tool-agnostic, portable, and developer-owned**: `LOOP-STATE.json`, durable memory, cross-tool adapters, and loop engineering.
- Cindy's strongest signal is **user effort reduction**: if LoopDesk asks the user to hand-craft connectors constantly, Cindy's client UX will feel materially better.
- Cindy's parallel task and review capability is flavorful, but LoopDesk does not need to mirror Orca's multi-worker desktop shell to gain that value; it only needs bounded sub-task/review runtime behavior.
- Cindy's skill + plugin boundary is mature; LoopDesk should keep skills and MCP first-class, but avoid Cindy's plugin heavy-runtime architecture unless cross-tool handoff demands it.

### 6.3 Gaps vs our direction
- Cindy is too **desktop/app-shell-first**, telemetry-connected, and officially cloud-backended for LoopDesk's strict local-first positioning.
- Cindy's cross-harness continuity is useful, but it is still continuity inside Cindy's world, not portable `LOOP-STATE.json` handoff among Claude Code, Codex, Trae, and similar external tools.
- Cindy's plugin marketplace and mobile clients expand surface and governance complexity; v0.1/v0.2 LoopDesk should avoid channel-first, mobile-first, or marketplace-first distractions.
- Cindy explicitly governs desktop, mobile, device-link, orca-workflow, maker-core, and plugin boundaries through authoritative `docs/`; this is mature product governance, but it also locks in a heavier client surface than LoopDesk's minimal runtime goal.
- Cindy treats scheduled work as a refined product feature; LoopDesk should preserve loop/goal autonomy but keep it simpler and more personal.

## 7. Recommendations

- Treat Cindy as the primary signal for **first-run ease-of-use, model/harness abstraction, multi-device continuity UX, structured plugin contracts, and desktop/mobile parity**.
- Do not treat Cindy as a direct product model to clone.
- Recommended LoopDesk focus:
  - preserve local-first workspace files, `LOOP-STATE.json`, and adapter-first cross-tool continuity
  - improve installation, auth, and first-loop storytelling so the product feels as approachable as Cindy without copying its shell
  - keep MCP/skill extension light, audit-first, and developer-inspectable
  - borrow Cindy's governance discipline for adapter/docs/schema boundaries without adopting its heavy Electron client surface
  - retain lightweight CLI + local Web UI instead of heavy Electron/mobile packaging
- Recommended guardrail:
  - avoid mandatory cloud account, telemetry-default, mobile-first surface, plugin marketplace, and Orca-style multi-worker shell as core v0.1/v0.2 public surface

## 8. Open Questions

- Confirm whether Cindy exposes durable cross-tool loop-state exports beyond its own desktop/mobile sessions.
- Confirm whether the open client repo supports offline/skip-signin workflows that preserve session, skill, and memory continuity across external coding CLIs.
- Confirm whether Cindy's future native harness changes cross-tool openness or reinforces its own platform lock-in.
- Confirm pricing, data handling, and privacy detail differences between hosted cloud use and from-source local builds.
- Confirm whether Cindy's plugin marketplace remains open versus gated, and whether LoopDesk can safely reference its plugin contract patterns without legal/license friction.


## 9. Primary Evidence Notes

- `README.md` and `README.zh-CN.md` both describe this repo as the open-source **client** for Cindy and call out desktop/mobile/shared packages plus `cindy-protocol`.
- `README.md` explicitly documents the **Skip Sign-In** mode: choosing it lets users use **local agents** without a Cindy account, while server-backed capabilities are unavailable in that state.
- `README.zh-CN.md` labels the two editions as **中国大陆版** and **国际版**, and `docs/product-rules/region-and-editions.md` makes the default/global-vs-cn identity rule explicit.
- `docs/README.md` declares the authoritative docs split across `product-rules/`, `dev-rules/`, and `design-rules/`.
- `docs/product-rules/core-product-principles.md` treats multi-device continuity as a first-class principle: switching devices or reconnecting should not force users to re-explain existing context.
- `docs/dev-rules/repo-map.md` confirms shared-package boundaries like `maker-core`, `orca-workflow`, `device-link`, and the desktop/mobile split.
- `AGENTS.md` explicitly says this repo负责 desktop、mobile 及其共享 packages，且服务端位于独立仓库；业务规则通过 `docs/` 索引维护。
