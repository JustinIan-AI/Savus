"""Personal workflow templates for LoopDesk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PersonalWorkflowTemplate:
    id: str
    name: str
    description: str
    loop_steps: List[str]
    goal_steps: List[str]
    roles: List[str]


PERSONAL_LOOP_TEMPLATES = [
    PersonalWorkflowTemplate(
        id="product-manager",
        name="Product Manager Workflow",
        description="Turn product ideas and feedback into validated Goals.",
        loop_steps=[
            "Collect user feedback and market signals.",
            "Prioritize problems by value and confidence.",
            "Draft a decision document with success metrics.",
        ],
        goal_steps=[
            "Write a bounded Goal for the chosen problem.",
            "Create acceptance criteria and stop condition.",
            "Review result against success metrics.",
        ],
        roles=["product manager"],
    ),
    PersonalWorkflowTemplate(
        id="architect",
        name="Architecture Sweep",
        description="Review architecture risks and convert findings into executable tasks.",
        loop_steps=[
            "Scan current architecture for risk and debt.",
            "Classify findings as act, propose, or escalate.",
            "Pick one bounded architectural task.",
        ],
        goal_steps=[
            "Document the architectural change.",
            "Implement or validate in an isolated worktree.",
            "Record lessons and update conventions.",
        ],
        roles=["architect"],
    ),
    PersonalWorkflowTemplate(
        id="backend-engineer",
        name="Backend Implementation",
        description="Deliver a bounded backend change with maker/checker verification.",
        loop_steps=[
            "Review failing tests, issues, and task backlog.",
            "Choose one backend task with clear acceptance criteria.",
            "Prepare tool context and worktree isolation.",
        ],
        goal_steps=[
            "Implement the bounded backend change.",
            "Run maker checks and targeted tests.",
            "Run checker verification and export result.",
        ],
        roles=["backend engineer"],
    ),
    PersonalWorkflowTemplate(
        id="frontend-engineer",
        name="Frontend Implementation",
        description="Deliver a bounded frontend change with review-ready evidence.",
        loop_steps=[
            "Review UI bugs, design feedback, and task backlog.",
            "Choose one frontend task with clear acceptance criteria.",
            "Prepare screenshots, design notes, and context.",
        ],
        goal_steps=[
            "Implement the bounded UI change.",
            "Validate visual and functional acceptance criteria.",
            "Record result, diff, and follow-up items.",
        ],
        roles=["frontend engineer"],
    ),
    PersonalWorkflowTemplate(
        id="test-engineer",
        name="Quality and Test Workflow",
        description="Turn quality signals into verified fixes or improvements.",
        loop_steps=[
            "Review failed tests, flaky signals, and coverage gaps.",
            "Classify quality issues by severity and owner.",
            "Select one bounded quality task.",
        ],
        goal_steps=[
            "Implement or adjust the fix or test change.",
            "Run focused verification and regression checks.",
            "Record flakiness, root cause, and prevention steps.",
        ],
        roles=["test engineer"],
    ),
]


def list_personal_templates() -> List[PersonalWorkflowTemplate]:
    return list(PERSONAL_LOOP_TEMPLATES)


def load_personal_template(template_id: str) -> PersonalWorkflowTemplate:
    for template in PERSONAL_LOOP_TEMPLATES:
        if template.id == template_id:
            return template
    raise KeyError(f"Unknown personal workflow template: {template_id}")
