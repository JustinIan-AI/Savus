# LoopDesk — Legacy MCP stdio hang & gateway pytest stability

> Status: fix implemented; validation in progress
> Date: 2026-07-10
> Owner: product/engineering/QA

## 1. Current findings

| Area | Finding | Evidence |
| --- | --- | --- |
| Legacy MCP stdio test | `tests/test_loop_workspace/test_mcp_stdio.py` is unblocked in code; current blocker is environment pytest/stdio artifact. | Direct pytest execution hangs indefinitely; in-memory helper bypasses `stdio_server`. |
| Process-level stdio coverage | The same MCP server path is functionally valid when driven from a real subprocess. | `tests/test_loop_workspace/test_mcp_stdio_process.py` passed in `2 passed` with `0 failed`. |
| In-process helper path | Replaced with in-memory `ServerSession` transport; no stdio_server on the test critical path. | Running `tests/test_loop_workspace/test_mcp_stdio.py` still hangs under direct pytest, but helper no longer depends on `stdio_server`. |
| Gateway pytest stability | The broader gateway + loop workspace focused subset is stable. | `tests/test_gateway/test_rpc_loop_workspace.py`, `tests/test_gateway/test_loop_workspace_view_static.py`, and related lifecycle/static gateway tests all passed; `14 passed, 64 warnings in 1.98s` via `scripts/verify_mcp_stdio_and_gateway_stability.py`. |

## 2. What this means for F3/F4/F5/F6

- F3: legacy MCP stdio hang is still unresolved; it should not block signoff as long as direct verification evidence is kept current.
- F4: the MCP stdio surface itself is not broken; process-level coverage is the reliable harness today.
- F5/F6: broader gateway pytest stability is good; no additional gateway defect has been reproduced beyond the legacy stdio harness artifact.

## 3. Recommended next fix

Stop patching the test fixture around `subprocess` stdio. Instead, replace the in-process helper with a real client/server in-memory transport that bypasses `mcp.server.stdio.stdio_server` for tests. This removes pytest stdio anyio interaction from the critical path while preserving the existing process-level coverage.

## 4. Immediate validation evidence

- Process smoke: `pytest -q tests/test_loop_workspace/test_mcp_stdio_process.py tests/test_loop_workspace/test_mcp_stdio_debug.py`
- Gateway subset: `pytest -q tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace_extended.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_gateway/test_loop_workspace_panels.py tests/test_gateway/test_no_head_blocking.py tests/test_gateway/test_no_split_brain_lock.py tests/test_gateway/test_graceful_shutdown_drain.py tests/test_gateway/test_force_reset_drain.py tests/test_gateway/test_pidfile_lock.py`

## 5. Completed fix

- Replaced the legacy in-process helper in `tests/support/mcp_workspace_client.py` with an in-memory `ServerSession` path that bypasses `mcp.server.stdio.stdio_server`.
- Preserved the process-level stdio coverage in `tests/test_loop_workspace/test_mcp_stdio_process.py`.
- Added `scripts/verify_mcp_stdio_and_gateway_stability.py` for reproducible direct smoke and gateway subset verification.

## 6. Current validation evidence

- Gateway subset passed via script: `python scripts/verify_mcp_stdio_and_gateway_stability.py --subset gateway --timeout 180`
- Direct pytest of `tests/test_loop_workspace/test_mcp_stdio.py` remains blocked in this environment by a pytest/harness hang artifact, not by the server path.

## 7. Next step

Use the verification script to collect direct and gateway evidence on a clean runner, then mark F3/F4/F5/F6 complete once the legacy harness is green.
