from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACES = [
    ROOT / "src" / "loopdesk" / "cli" / "skills_cmd.py",
    ROOT / "src" / "loopdesk" / "gateway" / "static" / "js" / "views" / "skills.js",
    ROOT / "src" / "loopdesk" / "skills" / "hub" / "__init__.py",
    ROOT / "src" / "loopdesk" / "skills" / "hub" / "clawhub.py",
    ROOT / "src" / "loopdesk" / "skills" / "hub" / "source.py",
]


def test_clawhub_copy_uses_community_source_language() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SURFACES)
    lower = combined.lower()

    assert "official marketplace" not in lower
    assert "loopdesk marketplace" not in lower
    assert "marketplace" not in lower
    assert "community" in lower
    assert "clawhub community source" in lower
