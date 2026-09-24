from __future__ import annotations

import os
import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from loopdesk.assets.models import AssetMetadata, AssetType

class AssetConflictError(Exception):
    """Raised when incoming team asset conflicts with modified local asset."""
    pass

class AssetDistributor:
    """Manages distribution, role scoping, env interpolation, and version pinning of team assets."""
    def __init__(self) -> None:
        self.pinned_versions: Dict[str, str] = {}
        self.installed_hashes: Dict[str, str] = {}

    def _get_target_path(self, asset: AssetMetadata, target_project_dir: Path) -> Path:
        if asset.type == AssetType.RULE:
            return target_project_dir / ".loopdesk" / "rules" / f"{asset.id}.md"
        elif asset.type == AssetType.SKILL:
            return target_project_dir / ".loopdesk" / "skills" / asset.id / "SKILL.md"
        elif asset.type == AssetType.SPEC:
            return target_project_dir / ".loopdesk" / "specs" / f"{asset.id}.md"
        elif asset.type == AssetType.MCP:
            return target_project_dir / ".loopdesk" / "mcp" / f"{asset.id}.json"
        return target_project_dir / ".loopdesk" / "assets" / asset.id

    def distribute(self, asset: AssetMetadata, target_project_dir: Path) -> Dict[str, Any]:
        target_path = self._get_target_path(asset, target_project_dir)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(asset.content, encoding="utf-8")
        
        content_hash = hashlib.sha256(asset.content.encode("utf-8")).hexdigest()
        self.installed_hashes[f"{target_project_dir}:{asset.id}"] = content_hash

        return {
            "status": "installed",
            "asset_id": asset.id,
            "path": str(target_path),
            "version": asset.version
        }

    def check_conflict(
        self,
        asset: Optional[AssetMetadata] = None,
        target_project_dir: Optional[Path] = None,
        asset_name: Optional[str] = None,
        local_hash: Optional[str] = None,
        incoming_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        # Legacy signature support for test_role_scope_and_conflict
        if asset_name is not None and local_hash is not None and incoming_hash is not None:
            expected = self.pinned_versions.get(asset_name)
            if expected and local_hash != expected and local_hash != incoming_hash:
                raise AssetConflictError(
                    f"Asset {asset_name} was modified locally (hash {local_hash} != expected {expected}) and differs from incoming {incoming_hash}."
                )
            return {"has_conflict": False}

        if asset is None or target_project_dir is None:
            return {"has_conflict": False}

        target_path = self._get_target_path(asset, target_project_dir)
        if not target_path.exists():
            return {"has_conflict": False, "local_modified": False}

        current_content = target_path.read_text(encoding="utf-8")
        current_hash = hashlib.sha256(current_content.encode("utf-8")).hexdigest()
        recorded_hash = self.installed_hashes.get(f"{target_project_dir}:{asset.id}")

        if recorded_hash and current_hash != recorded_hash:
            return {
                "has_conflict": True,
                "local_modified": True,
                "current_hash": current_hash,
                "recorded_hash": recorded_hash
            }

        return {"has_conflict": False, "local_modified": False}

    def filter_by_role(self, assets: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        return [a for a in assets if role in a.get("roles", [])]

    def resolve_env_placeholders(self, template: Dict[str, Any], env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        source_env = os.environ if env is None else env
        result: Dict[str, Any] = {}

        def _substitute(val: Any) -> Any:
            if isinstance(val, str):
                return re.sub(r'\$\{([^}]+)\}', lambda m: source_env.get(m.group(1), m.group(0)), val)
            elif isinstance(val, dict):
                return {k: _substitute(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [_substitute(x) for x in val]
            return val

        for k, v in template.items():
            result[k] = _substitute(v)
        return result

    def pin_asset(self, asset_name: str, expected_hash: str) -> None:
        self.pinned_versions[asset_name] = expected_hash
