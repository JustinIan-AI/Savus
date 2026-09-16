# Decision — Open-Source Reference Reuse for LoopDesk

> Status: Approved for v1.0 direction
> Owner: Product / Engineering
> Last updated: 2026-07-22
> Input: `docs/prd/personal-loop-workspace.md`, `docs/features/core-feature-list.md`, `docs/decisions/product-strategy.md`, `docs/decisions/desktop-web-im-product-boundary.md`, `docs/decisions/module-audit-loopdesk-vs-loopdesk.md`, `docs/research/competitive-intel-generalaction-emdash.md`, `docs/research/competitive-intel-openbmb-pilotdeck.md`, `docs/research/competitive-intel-dataelement-bisheng.md`, `docs/research/competitive-intel-proma.md`

## 1. Decision

LoopDesk v1.0 **borrows patterns and module ideas** from selected open-source repositories, but **does not adopt any inspected external repository as the direct base for forking or rebranding into LoopDesk**.

The recommended reuse posture is:

- **Reference first, not base-first.**
- **Extract bounded patterns** that strengthen `LOOP-STATE.json`, cross-tool adapters, loop engineering, and local-first control.
- **Avoid inheriting product narratives** that push LoopDesk toward heavy desktop shells, team-first workspaces, cloud rooms, or enterprise operations platforms.

## 2. Rationale

- LoopDesk v1.0 is defined as a **personal, local-first, portable loop workspace**, not a general-purpose agent IDE, team collaboration suite, or enterprise LLMOps platform；LoopDesk 不做 team room。
- `docs/prd/personal-loop-workspace.md` explicitly treats LoopDesk as runtime blood-pack material only; this decision extends that discipline to external repos.
- External repos reviewed so far are stronger as **adjacent references** than as **direct bases**, because each one centers a different product gravity:
  - desktop shell / agent runtime visibility
  - workspace-first agent OS
  - enterprise workflow / RAG / governance platform
  - chat-first / desktop-first workbench
- Forking any one of them as LoopDesk's base would likely import unwanted surface area, narrative drift, and maintenance debt before LoopDesk's own loop-state and adapter strategy is stable.

## 3. Boundary

- **In scope for reuse:** isolated patterns, interaction mental models, permission/approval structures, workflow primitives, memory/skill scoping rules, provider abstraction ideas, packaging/distribution references, and observability naming conventions.
- **Out of scope for reuse:** full product rebranding, wholesale runtime adoption, inherited brand narratives, default team/multi-user assumptions, cloud-first sync models, and heavy desktop/enterprise defaults.
- **Decision authority:** LoopDesk owns the v1.0 product surface; external references may inform implementation, but they cannot override local-first, portable-state, or cross-tool continuity requirements.

## 4. Borrow

| Source | Borrowable Pattern / Module | LoopDesk Mapping |
| --- | --- | --- |
| `generalaction/emdash` | Git worktree-per-task isolation and parallel exploration UX | Per-loop worktree or scratch isolation; branch/diff-aware loop state |
| `generalaction/emdash` | Issue/ticket -> task creation mental model | `project -> loop -> goal -> task` creation and intake flow |
| `generalaction/emdash` | Local diff/PR review and run-result inspection | Loop run log, maker/checker review, artifact/diff inspection |
| `generalaction/emdash` | Multi-provider CLI discovery and local runtime control | Cross-tool adapter layer for Claude Code, Codex, Codebuddy, Trae, Gemini |
| `OpenBMB/PilotDeck` | WorkSpace-scoped file, memory, and skill isolation | Project-scoped memory, skills, artifacts, and MCP binding |
| `OpenBMB/PilotDeck` | White-box editable memory and traceability | Durable memory index, edit/delete/pin decisions, auditable context |
| `OpenBMB/PilotDeck` | Smart routing across model tiers | Cost-aware model/provider routing and task difficulty routing |
| `OpenBMB/PilotDeck` | Always-on background work with file-backed results | Scheduler, background loop work, durable artifact output |
| `OpenBMB/PilotDeck` | MCP-native extension and lifecycle hook model | MCP server lifecycle, plugins, skills, and custom memory providers |
| `dataelement/bisheng` | Workflow DAG with loops, parallelism, batch, conditions | Complex loop workflow orchestration inside LoopDesk |
| `dataelement/bisheng` | Knowledge ingest, chunk, version, and retrieval patterns | Memory compaction, durable context, retrieval, and workspace memory hygiene |
| `dataelement/bisheng` | Permission, approval, audit, and observability naming | Approval queue, run log, cost observability, diagnostics, replay |
| `dataelement/bisheng` | v1/v2 API layering and external integration boundary | Gateway surface, internal RPC, external adapter boundary |
| `proma-ai/proma` | Workspace-scoped Skills/MCP configuration | Per-project skills, MCP binding, denylist, provider configuration |
| `proma-ai/proma` | Lightweight bounded remote continuation surface | Optional IM/web continuation for approved workspace work only |
| `proma-ai/proma` | Task interaction mental model | Task-oriented UI/runtime behavior instead of free-floating chat |

## 5. Do Not Borrow

| Source | Do-Not-Borrow Pattern | Reason |
| --- | --- | --- |
| `generalaction/emdash` | Heavy Electron desktop shell as the primary product surface | LoopDesk v1.0 remains CLI + local web gateway first; desktop packaging is future distribution, not current identity |
| `generalaction/emdash` | Cloud/enterprise-first or SaaS runtime narrative | Violates local-first authority and `LOOP-STATE.json` ownership |
| `OpenBMB/PilotDeck` | Full agent OS / multi-surface platform strategy | LoopDesk is a personal loop workspace, not a general-purpose agent operating system |
| `OpenBMB/PilotDeck` | Team/workspace governance as core state model | v1.0 excludes multi-user collaboration and team rooms |
| `OpenBMB/PilotDeck` | Heavy multi-surface CLI/Web/Desktop/IM parity investment | Web/IM remain secondary; Desktop is future distribution target |
| `dataelement/bisheng` | Enterprise LLMOps platform as product identity | Too heavy, team-oriented, and infra-heavy for solo developer loop workspace |
| `dataelement/bisheng` | Mandatory enterprise stack defaults | LoopDesk must preserve lightweight local onboarding and operation |
| `dataelement/bisheng` | Team governance, SSO/LDAP, org trees as primary complexity | Defer to later phases if ever; not v1.0 product primitives |
| `proma-ai/proma` | Desktop Chat/Agent shell as the main narrative | LoopDesk wins on portable loop state, not desktop chat richness |
| `proma-ai/proma` | Chat-first execution semantics | LoopDesk uses task/goal/loop semantics with maker/checker discipline |

## 6. Implementation Rule

- Any external pattern proposed for LoopDesk must pass three checks:
  1. Does it make `LOOP-STATE.json` more inspectable, portable, or durable?
  2. Does it strengthen cross-tool adapter or loop engineering behavior without importing unwanted product narrative?
  3. Can it be implemented as a bounded module or pattern, instead of inheriting a full external runtime or surface?
- If the answer is **no**, treat the source as competitive signal only, not implementation base.

## 7. Next Actions

- Convert this decision into module-level acceptance criteria for:
  - worktree isolation
  - workflow orchestration
  - memory/skill scoping
  - MCP lifecycle
  - approval/observability naming
- Review future open-source candidates against this document before adding them to `docs/research/`.
- Revisit this decision only if LoopDesk explicitly changes scope from personal local-first loop workspace to platform/team/enterprise product.
