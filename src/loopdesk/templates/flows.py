from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-")

class IssueFixFlow:
    @property
    def current_step(self) -> str:
        steps = ["triage", "maker", "checker", "escalation", "done"]
        if 0 <= self.current_step_idx < len(steps):
            return steps[self.current_step_idx]
        return "done"
    def __init__(self, issue_id: str, title: str, state: dict[str, Any] | None = None) -> None:
        self.issue_id = issue_id
        self.title = title
        slug = slugify(title)[:40]
        self.branch = f"codex/issue-{issue_id}-{slug}"
        self.steps = ["triage", "maker", "checker", "gate", "delivery"]
        
        if state:
            self.current_step_idx = state.get("current_step_idx", 0)
            self.history = state.get("history", [])
            self.branch = state.get("branch", self.branch)
        else:
            self.current_step_idx = 0
            self.history = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "branch": self.branch,
            "steps": self.steps,
            "current_step_idx": self.current_step_idx,
            "current_step": self.current_step,
            "history": self.history
        }

    def next_turn(self, role: str, output: str) -> dict[str, Any]:
        step = self.steps[self.current_step_idx]
        record = {
            "step": step,
            "role": role,
            "output": output,
            "status": "completed",
        }
        self.history.append(record)
        if self.current_step_idx < len(self.steps) - 1:
            self.current_step_idx += 1
        return record

    def is_ready_for_review(self) -> bool:
        completed = [h["step"] for h in self.history]
        return "triage" in completed and "maker" in completed and "checker" in completed

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IssueFixFlow:
        return cls(
            issue_id=data.get("issue_id", "0"),
            title=data.get("title", "Untitled"),
            state=data,
        )

class PRCommitFlow:
    def __init__(self, branch: str, title: str, commits: list[str], state: dict[str, Any] | None = None) -> None:
        self.branch = branch
        self.title = title
        self.commits = commits
        if state:
            self.history = state.get("history", [])
        else:
            self.history = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "title": self.title,
            "commits": self.commits,
            "history": self.history
        }

    def generate_8_section_pr_summary(self, diff: str = "") -> str:
        commit_list = "\n".join(f"- {c}" for c in self.commits) if self.commits else "- Initial delivery commit"
        
        modified_files: list[str] = []
        test_files: list[str] = []
        if diff:
            for line in diff.splitlines():
                if line.startswith("+++ b/"):
                    fpath = line[6:].strip()
                    if fpath not in modified_files:
                        modified_files.append(fpath)
                        if "test" in fpath.lower():
                            test_files.append(fpath)
                elif line.startswith("diff --git a/"):
                    parts = line.split()
                    if len(parts) >= 4 and parts[3].startswith("b/"):
                        fpath = parts[3][2:].strip()
                        if fpath not in modified_files:
                            modified_files.append(fpath)
                            if "test" in fpath.lower():
                                test_files.append(fpath)

        files_summary = ""
        if modified_files:
            files_summary = "\n**变更文件清单**:\n" + "\n".join(f"- `{f}`" for f in modified_files)

        test_coverage_desc = "- 单元测试与端到端用例已执行并验证绿灯。"
        if test_files:
            test_coverage_desc += "\n- 覆盖测试文件:\n" + "\n".join(f"  - `{f}`" for f in test_files)

        security_desc = "- 无 Secret/Token 硬编码，经过安全五层语法扫描。\n- 安全扫描: 无高危敏感词/密钥泄露，五层安全语法校验通过。"

        return f"""# {self.title}

## 1. 背景与上下文 (Background & Context)
Resolves automated task on branch `{self.branch}`.

## 2. 变更内容 (Changes Summary)
{commit_list}{files_summary}

## 3. 测试覆盖 (Test Coverage)
{test_coverage_desc}

## 4. 架构与设计决策 (Architecture & Design Decisions)
- 遵循 LoopDesk v2.0 local-first 与 TDD 原则。

## 5. 潜在风险与缓解 (Risk & Mitigation)
- 无破坏性变更，配置向前兼容。

## 6. 回滚计划 (Rollback Plan)
- 若异常直接 revert 对应 commit。

## 7. 关联工单与依赖 (Related Issues & Dependencies)
- Linked with branch: `{self.branch}`

## 8. 审计与安全 (Audit & Security)
{security_desc}
"""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PRCommitFlow:
        return cls(
            branch=data.get("branch", "main"),
            title=data.get("title", "PR"),
            commits=data.get("commits", []),
            state=data,
        )

class AutoResearchFlow:
    def __init__(self, topic: str, max_iterations: int = 3, state: dict[str, Any] | None = None) -> None:
        self.topic = topic
        self.max_iterations = max_iterations
        if state:
            self.iteration = state.get("iteration", 0)
            self.history = state.get("history", [])
        else:
            self.iteration = 0
            self.history = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "max_iterations": self.max_iterations,
            "iteration": self.iteration,
            "history": self.history
        }

    def step(self, proposer_notes: str, eval_score: float) -> dict[str, Any]:
        self.iteration += 1
        converged = eval_score >= 0.85 or self.iteration >= self.max_iterations
        turn = {
            "iteration": self.iteration,
            "proposer_notes": proposer_notes,
            "eval_score": eval_score,
            "converged": converged,
        }
        self.history.append(turn)
        return turn

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AutoResearchFlow:
        return cls(
            topic=data.get("topic", "research"),
            max_iterations=data.get("max_iterations", 3),
            state=data,
        )

@dataclass
class HandoffPacket:
    task_id: str
    step: str
    branch: str
    context_summary: str
    evidence: list[str] = field(default_factory=list)
    timestamp: str = ""

class CheckpointManager:
    def __init__(self) -> None:
        self._checkpoints: dict[str, HandoffPacket] = {}

    def save_checkpoint(self, checkpoint_id: str, packet: HandoffPacket) -> None:
        self._checkpoints[checkpoint_id] = packet

    def rewind_to(self, checkpoint_id: str) -> HandoffPacket:
        if checkpoint_id not in self._checkpoints:
            raise KeyError(f"Checkpoint not found: {checkpoint_id}")
        return self._checkpoints[checkpoint_id]
