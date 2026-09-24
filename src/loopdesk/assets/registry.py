from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional
import yaml
from loopdesk.assets.models import AssetMetadata, AssetType

class AssetRegistry:
    def __init__(self, root_dir: Path | str | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self._assets: dict[str, AssetMetadata] = {}

    def add(self, asset: AssetMetadata) -> None:
        self._assets[asset.id] = asset

    def get(self, asset_id: str) -> AssetMetadata | None:
        return self._assets.get(asset_id)

    def list_all(self) -> list[AssetMetadata]:
        return list(self._assets.values())

    def filter(
        self,
        asset_type: AssetType | None = None,
        role: str | None = None,
        tag: str | None = None,
    ) -> list[AssetMetadata]:
        results = list(self._assets.values())
        if asset_type:
            results = [a for a in results if a.type == asset_type]
        if role:
            results = [a for a in results if role in a.roles]
        if tag:
            results = [a for a in results if tag in a.tags]
        return results

    def discover(self) -> list[AssetMetadata]:
        found: list[AssetMetadata] = []
        if not self.root_dir.exists():
            return found

        # Scan rules
        rules_dir = self.root_dir / "rules"
        if rules_dir.exists():
            for p in rules_dir.glob("*.md"):
                content = p.read_text(encoding="utf-8", errors="replace")
                asset_id = p.stem
                asset_name = p.stem.replace("-", " ").title()
                roles = ["maker", "checker"]
                if content.startswith("---"):
                    parts = content.split("---")
                    if len(parts) >= 3:
                        try:
                            meta = yaml.safe_load(parts[1]) or {}
                            if isinstance(meta, dict):
                                asset_id = meta.get("id", asset_id)
                                asset_name = meta.get("name", asset_name)
                                roles = meta.get("roles", roles)
                        except Exception:
                            pass
                asset = AssetMetadata(
                    id=asset_id,
                    name=asset_name,
                    type=AssetType.RULE,
                    content=content,
                    roles=roles
                )
                self.add(asset)
                found.append(asset)

        # Scan specs
        specs_dir = self.root_dir / "specs"
        if specs_dir.exists():
            for p in specs_dir.glob("*.md"):
                content = p.read_text(encoding="utf-8", errors="replace")
                asset_id = p.stem
                asset_name = p.stem.replace("-", " ").title()
                roles = ["maker"]
                if content.startswith("---"):
                    parts = content.split("---")
                    if len(parts) >= 3:
                        try:
                            meta = yaml.safe_load(parts[1]) or {}
                            if isinstance(meta, dict):
                                asset_id = meta.get("id", asset_id)
                                asset_name = meta.get("name", asset_name)
                                roles = meta.get("roles", roles)
                        except Exception:
                            pass
                asset = AssetMetadata(
                    id=asset_id,
                    name=asset_name,
                    type=AssetType.SPEC,
                    content=content,
                    roles=roles
                )
                self.add(asset)
                found.append(asset)
        return found
