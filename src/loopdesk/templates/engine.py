from __future__ import annotations

import ast
import operator
from typing import Any
from loopdesk.templates.manifest import TemplateManifest, TemplateStep, TemplateInput

class SafeConditionEvaluator:
    """Safely evaluates stop condition expressions like 'tests_pass == True', 'score >= 0.85'."""
    OPS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }

    @classmethod
    def evaluate(cls, expr: str, context: dict[str, Any]) -> bool:
        expr = expr.strip()
        if not expr:
            return False
        try:
            tree = ast.parse(expr, mode="eval")
            return bool(cls._eval_node(tree.body, context))
        except Exception:
            return False

    @classmethod
    def _eval_node(cls, node: ast.AST, context: dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return context.get(node.id, False)
        elif isinstance(node, ast.Compare):
            left = cls._eval_node(node.left, context)
            for op_type, comparator in zip(node.ops, node.comparators):
                op_fn = cls.OPS.get(type(op_type))
                if not op_fn:
                    return False
                right = cls._eval_node(comparator, context)
                if not op_fn(left, right):
                    return False
                left = right
            return True
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not cls._eval_node(node.operand, context)
        return False

class TemplateEngine:
    def __init__(self) -> None:
        self._templates: dict[str, TemplateManifest] = {}

    def register(self, manifest: TemplateManifest) -> None:
        self._templates[manifest.id] = manifest

    def get(self, template_id: str) -> TemplateManifest | None:
        return self._templates.get(template_id)

    def list_templates(self) -> list[TemplateManifest]:
        return list(self._templates.values())

    def evaluate_stop_conditions(self, template_id: str, context: dict[str, Any]) -> dict[str, Any]:
        manifest = self.get(template_id)
        if not manifest:
            raise ValueError(f"Unknown template: {template_id}")

        results = {}
        all_met = True
        for cond in manifest.stop_conditions:
            met = SafeConditionEvaluator.evaluate(cond, context)
            results[cond] = met
            if not met:
                all_met = False

        return {
            "template_id": template_id,
            "all_conditions_met": all_met,
            "condition_results": results,
            "context_evaluated": context
        }

    def register_builtin_templates(self) -> None:
        issue_fix = TemplateManifest(
            id="issue-fix",
            name="Issue Fix Standard Flow",
            version="2.0.0",
            description="Triage -> Maker -> Checker -> Gate -> Delivery 循环长任务模板",
            inputs=[
                TemplateInput(id="issue_id", label="Issue ID", required=True),
                TemplateInput(id="branch_name", label="Work Branch", default="codex/fix-{issue_id}"),
                TemplateInput(id="issue_url", label="Issue URL", default=""),
            ],
            steps=[
                TemplateStep(id="triage", name="Triage & Repro", role="triage", description="重现问题并编写最小失败用例"),
                TemplateStep(id="maker", name="Implement TDD Fix", role="maker", description="编写最小实现使测试通过"),
                TemplateStep(id="checker", name="Review & Verify", role="checker", description="执行完整测试套件收集证据"),
                TemplateStep(id="gate", name="Human Approval Gate", role="operator", description="人工审核代码修改与验证收据"),
                TemplateStep(id="delivery", name="PR & Delivery", role="delivery", description="创建 Pull Request 并关联工单"),
            ],
            stop_conditions=[
                "tests_pass == True",
                "no_regression == True",
                "review_gate_approved == True",
            ],
        )

        pr_commit = TemplateManifest(
            id="pr-commit",
            name="PR Commit & Review Packet",
            version="2.0.0",
            description="自动化整理变更集并生成 8 段式双语 PR 描述",
            inputs=[
                TemplateInput(id="pr_title", label="PR Title", required=True),
                TemplateInput(id="target_branch", label="Target Branch", default="main"),
            ],
            steps=[
                TemplateStep(id="diff_audit", name="Audit Git Diff", role="checker"),
                TemplateStep(id="summary_gen", name="Generate 8-section PR Summary", role="maker"),
                TemplateStep(id="gate", name="PR Operator Gate", role="operator"),
                TemplateStep(id="push", name="Git Push & Open PR", role="delivery"),
            ],
            stop_conditions=["diff_clean == True", "pr_summary_approved == True"],
        )

        auto_research = TemplateManifest(
            id="auto-research",
            name="Auto Research & Multi-agent Convergence",
            version="2.0.0",
            description="Proposer -> Executor -> Evaluator 闭环调研与方案收敛",
            inputs=[
                TemplateInput(id="research_topic", label="Topic", required=True),
                TemplateInput(id="max_iterations", label="Max Iterations", default="3"),
            ],
            steps=[
                TemplateStep(id="propose", name="Hypothesis & Plan", role="proposer"),
                TemplateStep(id="execute", name="Experiment & Collect", role="executor"),
                TemplateStep(id="evaluate", name="Score & Convergence Check", role="evaluator"),
            ],
            stop_conditions=["score >= 0.85", "iteration >= max_iterations"],
        )

        self.register(issue_fix)
        self.register(pr_commit)
        self.register(auto_research)

    def render_goal_skeleton(self, template_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manifest = self.get(template_id)
        if not manifest:
            raise ValueError(f"Unknown template: {template_id}")

        rendered_params: dict[str, Any] = {}
        for inp in manifest.inputs:
            val = params.get(inp.id)
            if val is None:
                val = inp.default
            if inp.required and not val:
                raise ValueError(f"Missing required parameter: {inp.id}")
            rendered_params[inp.id] = val

        branch = rendered_params.get("branch_name", "")
        if isinstance(branch, str) and "{issue_id}" in branch:
            branch = branch.replace("{issue_id}", str(rendered_params.get("issue_id", "")))

        return {
            "template_id": manifest.id,
            "template_name": manifest.name,
            "version": manifest.version,
            "params": rendered_params,
            "branch": branch,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "role": s.role,
                    "status": "pending",
                    "description": s.description,
                }
                for s in manifest.steps
            ],
            "stop_conditions": manifest.stop_conditions,
            "current_step_index": 0,
        }
