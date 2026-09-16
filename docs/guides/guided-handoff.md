# Guided Handoff — LoopDesk v1.1

LoopDesk keeps work coherent across Claude Code, Codex, Codebuddy, Trae, Gemini, and local CLIs by treating `LOOP-STATE.json` as the durable source of truth. Use this handoff order whenever you switch tools or resume an in-flight goal.

## First handoff

1. Select or confirm the active **project**.
2. Select or confirm the active **loop**.
3. Bind or resume the **worktree** for the current goal.
4. Resume the **goal** with the latest safe action.

## Commands

```sh
loopdesk workspace init <workspace-root>
loopdesk workspace project set <workspace-root> --name order-service
loopdesk workspace loop set <workspace-root> architecture-review
loopdesk workspace worktree <workspace-root> create --work-id order-service --json
loopdesk workspace resume <workspace-root> order-service --summary "..." --source external
```

## Anti-room guardrails

- Keep the narrative personal-first and local-first.
- Do not position team rooms, cloud sync, or IM-first chat as the primary workflow; LoopDesk 不做这些方向。
- Long-running or high-risk work stays owned by the local runtime; remote surfaces only inspect or continue approved bounded work.
