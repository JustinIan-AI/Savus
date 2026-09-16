"""LoopDesk v1.1 official runtime matrix and desktop packaging boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeCapabilityProfile:
    runtime_id: str
    label: str
    transport: str
    primary_interface: str
    supported: bool = True
    notes: tuple[str, ...] = ()
    capability_profile_keys: tuple[str, ...] = ("execute", "resume", "status", "cancel", "inspect")
    execute_input_schema: dict[str, str] = field(default_factory=lambda: {"task": "object", "workspace": "object"})
    resume_input_schema: dict[str, str] = field(default_factory=lambda: {"run_id": "string"})
    status_output_schema: dict[str, str] = field(default_factory=lambda: {"run_id": "string", "status": "string"})
    cancel_output_schema: dict[str, str] = field(default_factory=lambda: {"run_id": "string", "canceled": "bool"})
    inspect_output_schema: dict[str, str] = field(default_factory=lambda: {"run_id": "string", "artifacts": "array"})


@dataclass(frozen=True)
class DesktopPackagingBoundary:
    launcher_model: str = "local_runtime_plus_system_launcher"
    primary_runtime: str = "local_gateway"
    durable_state_owner: str = "local_workspace"
    excluded_models: tuple[str, ...] = (
        "electron_shell",
        "cloud_sync",
        "team_room",
        "saas_runtime",
    )
    launcher_responsibilities: tuple[str, ...] = (
        "start_local_gateway",
        "repair_local_runtime",
        "open_inspection_shortcuts",
        "preserve_local_workspace_data",
    )

    def is_excluded_model(self, model: str) -> bool:
        return model.lower().replace(" ", "_").replace("-", "_") in self.excluded_models


def get_supported_runtime_matrix() -> dict[str, Any]:
    profiles = [
        RuntimeCapabilityProfile(
            runtime_id="claude-code",
            label="Claude Code",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Primary local coding runtime.",),
        ),
        RuntimeCapabilityProfile(
            runtime_id="codex-cli",
            label="Codex CLI",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Primary local coding runtime.",),
        ),
        RuntimeCapabilityProfile(
            runtime_id="codebuddy",
            label="Codebuddy",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Supported local coding runtime.",),
        ),
        RuntimeCapabilityProfile(
            runtime_id="trae",
            label="Trae",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Supported local coding runtime.",),
        ),
        RuntimeCapabilityProfile(
            runtime_id="opencode",
            label="OpenCode",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Official v1.1 supported runtime.",),
        ),
        RuntimeCapabilityProfile(
            runtime_id="gemini",
            label="Gemini / Local CLIs",
            transport="native_cli",
            primary_interface="terminal",
            notes=("Supported local coding runtime.",),
        ),
    ]
    supported = {profile.runtime_id: profile for profile in profiles}
    return {
        "schema_version": 1,
        "official_support_policy": "supported",
        "default_primary_runtime": "claude-code",
        "runtimes": supported,
        "runtime_order": [profile.runtime_id for profile in profiles],
    }


def get_desktop_packaging_boundary() -> DesktopPackagingBoundary:
    return DesktopPackagingBoundary()
