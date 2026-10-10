from __future__ import annotations

import enum
import fnmatch
import hashlib
import json
import time
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


class GateType(str, enum.Enum):
    HEALTH = "health"
    OPERATOR = "operator"
    EVIDENCE = "evidence"
    FOCUS = "focus"
    QUOTA = "quota"


@dataclass
class ValidationReceipt:
    task_id: str
    project_id: str
    timestamp: float
    validation_command: str
    exit_code: int
    stdout_hash: str
    sha256_digest: str
    operator_decision: str
    operator_comment: str
    passed_gates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValidationReceipt:
        return cls(**data)


@dataclass
class GateContext:
    project_id: str
    task_id: str
    operator_decision: str = "approved"  # "approved" or "denied"
    operator_comment: str = ""
    validation_command: str = ""
    validation_exit_code: int = 0
    validation_stdout: str = ""
    touched_files: list[str] = field(default_factory=list)
    allowed_write_scopes: list[str] = field(default_factory=list)
    consumed_tokens: int = 0
    token_limit: int = 1000000
    execute_validation: bool = False
    cwd: Optional[str] = None


@dataclass
class GateVerdict:
    passed: bool
    failed_gate: Optional[GateType] = None
    reason: str = ""
    receipt: Optional[ValidationReceipt] = None


class FiveTierGateEngine:
    def __init__(self, force_health_unhealthy: Optional[str] = None):
        self._force_health_unhealthy = force_health_unhealthy

    def evaluate(self, ctx: GateContext) -> GateVerdict:
        passed_gates: list[str] = []

        # 1. Health Gate
        if self._force_health_unhealthy:
            return GateVerdict(
                passed=False,
                failed_gate=GateType.HEALTH,
                reason=f"Health Gate check failed: {self._force_health_unhealthy}",
            )
        passed_gates.append(GateType.HEALTH.value)

        # 2. Operator Gate
        if ctx.operator_decision.lower() != "approved":
            return GateVerdict(
                passed=False,
                failed_gate=GateType.OPERATOR,
                reason=f"Operator Gate denied: {ctx.operator_comment or 'Human rejection'}",
            )
        passed_gates.append(GateType.OPERATOR.value)

        # 3. Evidence Gate
        if not ctx.validation_command:
            return GateVerdict(
                passed=False,
                failed_gate=GateType.EVIDENCE,
                reason="Evidence Gate failed: No validation command specified",
            )
        exit_code = ctx.validation_exit_code
        stdout = ctx.validation_stdout
        if ctx.execute_validation:
            try:
                res = subprocess.run(
                    ctx.validation_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=ctx.cwd,
                    timeout=30,
                )
                exit_code = res.returncode
                stdout = res.stdout + ("\n" + res.stderr if res.stderr else "")
            except Exception as exc:
                return GateVerdict(
                    passed=False,
                    failed_gate=GateType.EVIDENCE,
                    reason=f"Evidence Gate failed: execution error {exc}",
                )
        if exit_code != 0:
            return GateVerdict(
                passed=False,
                failed_gate=GateType.EVIDENCE,
                reason=f"Evidence Gate failed: validation command returned exit code {exit_code}",
            )
        passed_gates.append(GateType.EVIDENCE.value)

        # 4. Focus Gate
        if ctx.allowed_write_scopes:
            for file_path in ctx.touched_files:
                matched = any(
                    fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path.lstrip("/"), pattern.lstrip("/"))
                    for pattern in ctx.allowed_write_scopes
                )
                if not matched:
                    return GateVerdict(
                        passed=False,
                        failed_gate=GateType.FOCUS,
                        reason=f"Focus Gate failed: Touched file '{file_path}' violates write scopes: {ctx.allowed_write_scopes}",
                    )
        passed_gates.append(GateType.FOCUS.value)

        # 5. Quota Gate
        if ctx.consumed_tokens > ctx.token_limit:
            return GateVerdict(
                passed=False,
                failed_gate=GateType.QUOTA,
                reason=f"Quota Gate failed: Quota exceeded ({ctx.consumed_tokens} > {ctx.token_limit} tokens)",
            )
        passed_gates.append(GateType.QUOTA.value)

        # All passed -> Issue ValidationReceipt
        now = time.time()
        stdout_hash = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        payload = f"{ctx.task_id}:{ctx.project_id}:{ctx.validation_command}:{exit_code}:{stdout_hash}:{now}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        receipt = ValidationReceipt(
            task_id=ctx.task_id,
            project_id=ctx.project_id,
            timestamp=now,
            validation_command=ctx.validation_command,
            exit_code=exit_code,
            stdout_hash=stdout_hash,
            sha256_digest=digest,
            operator_decision=ctx.operator_decision,
            operator_comment=ctx.operator_comment,
            passed_gates=passed_gates,
        )

        return GateVerdict(
            passed=True,
            receipt=receipt,
        )
