"""v1.2 runtime matrix tests for LoopDesk contracts and desktop boundary."""

from __future__ import annotations

import pytest

from loopdesk.loop_workspace.runtime_matrix import (
    RuntimeCapabilityProfile,
    get_desktop_packaging_boundary,
    get_supported_runtime_matrix,
)


def test_supported_matrix_exposes_v12_runtime_interface_contracts() -> None:
    matrix = get_supported_runtime_matrix()

    assert matrix["schema_version"] == 1
    assert matrix["default_primary_runtime"] == "claude-code"
    assert matrix["runtime_order"] == [
        "claude-code",
        "codex-cli",
        "codebuddy",
        "trae",
        "opencode",
        "gemini",
    ]

    claude_profile = matrix["runtimes"]["claude-code"]
    assert list(claude_profile.capability_profile_keys) == [
        "execute",
        "resume",
        "status",
        "cancel",
        "inspect",
    ]
    assert claude_profile.execute_input_schema == {"task": "object", "workspace": "object"}
    assert claude_profile.status_output_schema == {"run_id": "string", "status": "string"}


def test_desktop_boundary_remains_local_runtime_plus_system_launcher() -> None:
    boundary = get_desktop_packaging_boundary()

    assert boundary.launcher_model == "local_runtime_plus_system_launcher"
    assert boundary.primary_runtime == "local_gateway"
    assert boundary.durable_state_owner == "local_workspace"
    assert boundary.is_excluded_model("cloud-sync") is True
    assert boundary.is_excluded_model("team room") is True
    assert "start_local_gateway" in boundary.launcher_responsibilities


def test_official_runtime_profiles_preserve_v11_support_matrix() -> None:
    matrix = get_supported_runtime_matrix()

    for runtime_id, expected_label in [
        ("codex-cli", "Codex CLI"),
        ("codebuddy", "Codebuddy"),
        ("trae", "Trae"),
        ("opencode", "OpenCode"),
        ("gemini", "Gemini / Local CLIs"),
    ]:
        profile = matrix["runtimes"][runtime_id]
        assert isinstance(profile, RuntimeCapabilityProfile)
        assert profile.runtime_id == runtime_id
        assert profile.label == expected_label
        assert profile.transport == "native_cli"
        assert profile.primary_interface == "terminal"
