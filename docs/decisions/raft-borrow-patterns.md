# Decision — Raft Borrow Patterns for LoopDesk

> Status: Proposed
> Owner: Product / Engineering
> Last updated: 2026-07-22
> Input: `docs/research/competitive-intel-raft-docs.md`

## 1. Decision

Adopt Raft's **onboarding narrative, task-handoff mental model, and Markdown-first / LLM-friendly docs patterns** as inspiration for LoopDesk.

Do **not** adopt Raft's **room-first, team-first, shared-identity-first, or cloud-sync-first** product shape for LoopDesk v1.0；LoopDesk 不做这些方向。

## 2. Boundary

Raft is a useful reference for **UX narrative, docs ergonomics, and task-first onboarding**.
Raft is **not** the product model for LoopDesk because its visible center of gravity is a shared human-agent workspace, while LoopDesk remains a **personal, local-first, portable loop workspace** with durable `LOOP-STATE.json` authority.

## 3. Borrow

- Onboarding as a short narrative: create runtime, connect workspace, complete first useful loop.
- Task-handoff framing: agent work should return completed, reviewable results tied to `goal -> task -> run log -> artifact`.
- Docs-led first impression: welcome path should lead with the fastest route from install to a working loop.
- Markdown-first docs: keep public docs simple, editable, and agent-readable.
- Machine-readable doc surface: expose structured TOC or equivalent for future MCP/docs integration.
- Visibility language: map catch-up, search, and notification ideas to local loop state and approvals only.

## 4. Do Not Borrow

- Multi-user room or team-first collaboration as the main narrative.
- Shared agent identity, shared global memory, or room sync as core state primitives.
- Cross-device sync that weakens local `LOOP-STATE.json` authority.
- Heavy app-first design that buries CLI + local gateway authority.

## 5. Mapping

| Raft pattern | LoopDesk mapping |
| --- | --- |
| Onboarding agent | `loopdesk init / onboard wizard` |
| Hand off task | `loopdesk loop goal / task / run` |
| Catch up / search / pinged | `loop status + run log + artifact review + approval notification` |
| LLM-friendly docs | `docs/ + structured TOC + MCP docs surface` |
| Team room | Defer; bounded sharing may arrive later as an optional boundary |

## 6. Next Actions

- Add onboarding task flow to the next loop-workspace design review.
- Evaluate a lightweight `llms.txt` or doc-index endpoint for docs.
- Keep Web/IM surfaces read/approval focused; do not promote them to primary runtime.
