from __future__ import annotations

import pytest
from pathlib import Path
from loopdesk.assets.models import AssetMetadata, AssetType
from loopdesk.assets.registry import AssetRegistry

def test_asset_metadata_schema():
    asset = AssetMetadata(
        id="tdd-guard",
        name="TDD Guardrail Rule",
        type=AssetType.RULE,
        version="1.2.0",
        author="core-team",
        description="Enforces write-failing-tests-first discipline",
        tags=["quality", "tdd", "backend"],
        roles=["backend", "fullstack"],
        content="# TDD Guidelines\nAlways write test before implementation."
    )
    assert asset.id == "tdd-guard"
    assert asset.type == AssetType.RULE
    assert asset.version == "1.2.0"
    data = asset.to_dict()
    assert data["type"] == "rule"
    assert "content" in data

def test_asset_registry_scan_and_filter(tmp_path: Path):
    registry = AssetRegistry(root_dir=tmp_path)
    
    # Register assets
    rule = AssetMetadata(
        id="rule-code-style",
        name="Team Code Style",
        type=AssetType.RULE,
        version="1.0.0",
        roles=["frontend", "backend"],
        tags=["style"],
        content="Prefer explicit typing."
    )
    skill = AssetMetadata(
        id="skill-pr-review",
        name="PR Reviewer Skill",
        type=AssetType.SKILL,
        version="2.1.0",
        roles=["reviewer"],
        tags=["review"],
        content="Check security and performance."
    )
    mcp = AssetMetadata(
        id="mcp-jira",
        name="JIRA Connector Config",
        type=AssetType.MCP,
        version="1.0.0",
        roles=["backend"],
        tags=["jira", "connector"],
        content='{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-jira"]}'
    )
    
    registry.add(rule)
    registry.add(skill)
    registry.add(mcp)
    
    assert len(registry.list_all()) == 3
    # Filter by type
    assert len(registry.filter(asset_type=AssetType.SKILL)) == 1
    # Filter by role
    assert len(registry.filter(role="backend")) == 2
    # Filter by tag
    assert len(registry.filter(tag="review")) == 1
