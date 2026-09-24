from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class AssetType(str, Enum):
    RULE = "rule"
    SPEC = "spec"
    SKILL = "skill"
    MCP = "mcp"
    DELIVERABLE = "deliverable"

@dataclass
class AssetMetadata:
    id: str
    name: str
    type: AssetType
    version: str = "1.0.0"
    author: str = "team"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    content: str = ""
    checksum: str = ""
    source_repo: str = ""
    installed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, AssetType) else str(self.type),
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "tags": list(self.tags),
            "roles": list(self.roles),
            "content": self.content,
            "checksum": self.checksum,
            "source_repo": self.source_repo,
            "installed": self.installed,
        }
