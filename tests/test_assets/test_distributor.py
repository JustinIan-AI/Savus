from __future__ import annotations

import pytest
from pathlib import Path
from loopdesk.assets.models import AssetMetadata, AssetType
from loopdesk.assets.distributor import AssetDistributor

def test_distribute_asset_to_project_worktree(tmp_path: Path):
    distributor = AssetDistributor()
    
    # Target project directory
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()
    
    # 1. Distribute a Rule
    rule = AssetMetadata(
        id="rule-tdd",
        name="TDD Rule",
        type=AssetType.RULE,
        version="1.0.0",
        content="# TDD Rules\nStrict test-first required."
    )
    res_rule = distributor.distribute(asset=rule, target_project_dir=project_dir)
    assert res_rule["status"] == "installed"
    installed_rule = project_dir / ".loopdesk" / "rules" / "rule-tdd.md"
    assert installed_rule.exists()
    assert "Strict test-first required" in installed_rule.read_text()

    # 2. Distribute a Skill
    skill = AssetMetadata(
        id="skill-reviewer",
        name="Reviewer Skill",
        type=AssetType.SKILL,
        version="1.0.0",
        content="# Reviewer Skill instructions"
    )
    res_skill = distributor.distribute(asset=skill, target_project_dir=project_dir)
    assert res_skill["status"] == "installed"
    installed_skill = project_dir / ".loopdesk" / "skills" / "skill-reviewer" / "SKILL.md"
    assert installed_skill.exists()
    assert "Reviewer Skill instructions" in installed_skill.read_text()

def test_conflict_detection_and_manifest(tmp_path: Path):
    distributor = AssetDistributor()
    project_dir = tmp_path / "project_b"
    project_dir.mkdir()
    
    rule = AssetMetadata(
        id="rule-format",
        name="Format Rule",
        type=AssetType.RULE,
        version="1.0.0",
        content="Use ruff format."
    )
    distributor.distribute(asset=rule, target_project_dir=project_dir)
    
    # Now local file is modified by human
    installed_file = project_dir / ".loopdesk" / "rules" / "rule-format.md"
    installed_file.write_text("Custom user modifications!")
    
    # Distribute new version 2.0.0
    rule_v2 = AssetMetadata(
        id="rule-format",
        name="Format Rule",
        type=AssetType.RULE,
        version="2.0.0",
        content="Use ruff check and format v2."
    )
    conflict = distributor.check_conflict(asset=rule_v2, target_project_dir=project_dir)
    assert conflict["has_conflict"] is True
    assert conflict["local_modified"] is True
