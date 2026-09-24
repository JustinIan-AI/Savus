from __future__ import annotations

import pytest
from loopdesk.templates.manifest import TemplateManifest, TemplateStep, TemplateInput
from loopdesk.templates.engine import TemplateEngine

def test_template_manifest_schema():
    manifest = TemplateManifest(
        id="issue-fix",
        name="Issue Fix Standard Flow",
        version="2.0.0",
        inputs=[
            TemplateInput(id="issue_id", label="Issue ID", required=True),
            TemplateInput(id="branch_name", label="Work Branch", default="codex/fix-{issue_id}"),
        ],
        steps=[
            TemplateStep(id="triage", name="Triage & Repro", role="triage"),
            TemplateStep(id="maker", name="Implement TDD Fix", role="maker"),
            TemplateStep(id="checker", name="Review & Verify", role="checker"),
            TemplateStep(id="gate", name="Human Approval Gate", role="operator"),
            TemplateStep(id="delivery", name="PR & Delivery", role="delivery"),
        ],
        stop_conditions=["tests_pass == True", "no_regression == True"]
    )
    assert manifest.id == "issue-fix"
    assert len(manifest.steps) == 5

def test_render_goal_skeleton():
    engine = TemplateEngine()
    engine.register_builtin_templates()
    
    # Render issue-fix
    skeleton = engine.render_goal_skeleton(
        template_id="issue-fix",
        params={"issue_id": "104", "issue_url": "https://github.com/acme/repo/issues/104"}
    )
    assert skeleton["template_id"] == "issue-fix"
    assert skeleton["branch"] == "codex/fix-104"
    assert len(skeleton["steps"]) == 5
    assert skeleton["steps"][0]["id"] == "triage"
    assert skeleton["steps"][1]["id"] == "maker"
    assert "stop_conditions" in skeleton
