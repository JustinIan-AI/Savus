from __future__ import annotations

import json
from pathlib import Path
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.governance.gates import ValidationReceipt

def test_gate_receipt_persistence_in_loop_state(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()

    # 模拟任务创建
    service.upsert_task(
        "task-abc",
        title="Fix memory leak",
        status="in_review",
        project_id="proj-1",
    )

    receipt = ValidationReceipt(
        task_id="task-abc",
        project_id="proj-1",
        timestamp=1700000000.0,
        validation_command="pytest tests/",
        exit_code=0,
        stdout_hash="abcd1234hash",
        sha256_digest="digest5678",
        operator_decision="approved",
        operator_comment="LGTM",
        passed_gates=["health", "operator", "evidence", "focus", "quota"],
    )

    # 记录裁决凭证到 LOOP-STATE.json
    service.record_gate_receipt(receipt)

    # 校验持久化
    state = service.current_state()
    assert "gate_receipts" in state
    assert len(state["gate_receipts"]) == 1
    stored = state["gate_receipts"][0]
    assert stored["task_id"] == "task-abc"
    assert stored["sha256_digest"] == "digest5678"
    assert stored["passed_gates"] == ["health", "operator", "evidence", "focus", "quota"]

    # 对应任务状态同步更新为 completed
    task = next(t for t in state["tasks"] if t["id"] == "task-abc")
    assert task["gate_status"] == "passed"
    assert task["receipt_digest"] == "digest5678"
