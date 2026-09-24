from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class TemplateInput:
    id: str
    label: str
    required: bool = False
    default: str | None = None
    description: str = ""

@dataclass
class TemplateStep:
    id: str
    name: str
    role: str
    description: str = ""
    timeout_seconds: int = 3600

@dataclass
class TemplateManifest:
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    inputs: list[TemplateInput] = field(default_factory=list)
    steps: list[TemplateStep] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "inputs": [
                {
                    "id": i.id,
                    "label": i.label,
                    "required": i.required,
                    "default": i.default,
                    "description": i.description,
                }
                for i in self.inputs
            ],
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "role": s.role,
                    "description": s.description,
                    "timeout_seconds": s.timeout_seconds,
                }
                for s in self.steps
            ],
            "stop_conditions": list(self.stop_conditions),
        }
