from __future__ import annotations

import pytest
from loopdesk.assets.distributor import AssetDistributor, AssetConflictError
from loopdesk.assets.registry import AssetRegistry, AssetMetadata

def test_role_scope_filtering():
    distributor = AssetDistributor()
    assets = [
        {"name": "react-rules", "roles": ["frontend"], "tags": ["ui"]},
        {"name": "sql-optimizer", "roles": ["backend"], "tags": ["db"]},
        {"name": "general-coding", "roles": ["frontend", "backend"], "tags": ["core"]}
    ]

    frontend_assets = distributor.filter_by_role(assets, role="frontend")
    assert len(frontend_assets) == 2
    names = [a["name"] for a in frontend_assets]
    assert "react-rules" in names
    assert "general-coding" in names
    assert "sql-optimizer" not in names

def test_env_var_interpolation():
    distributor = AssetDistributor()
    template = {
        "mcp_server": "jira",
        "api_key": "${JIRA_SECRET_TOKEN}",
        "endpoint": "https://api.jira.com/${TENANT_ID}/v2"
    }
    env = {
        "JIRA_SECRET_TOKEN": "secret_abc_123",
        "TENANT_ID": "acme-corp"
    }

    resolved = distributor.resolve_env_placeholders(template, env=env)
    assert resolved["api_key"] == "secret_abc_123"
    assert resolved["endpoint"] == "https://api.jira.com/acme-corp/v2"

def test_version_pin_and_conflict_detection():
    distributor = AssetDistributor()
    # Pinned hash in workspace
    distributor.pin_asset("team-rule-1", expected_hash="hash_v1_original")

    # When trying to sync new version while local has conflicting uncommitted hash
    with pytest.raises(AssetConflictError):
        distributor.check_conflict(
            asset_name="team-rule-1",
            local_hash="hash_v1_modified_by_user",
            incoming_hash="hash_v2_team"
        )
