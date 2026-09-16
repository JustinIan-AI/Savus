"""Durable local memory helpers for personal LoopDesk workspaces."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DurableMemoryEntry:
    key: str
    title: str
    body: str
    tags: tuple[str, ...]
    source: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class MemorySearchHit:
    entry: DurableMemoryEntry
    score: float
    match: str


class DurableMemoryIndex:
    def __init__(self, root: Path, *, index_path: Path | None = None) -> None:
        self._root = root
        self._memory_dir = root / "memory"
        self._index_path = index_path or (self._memory_dir / "INDEX.md")
        self._memory_dir.mkdir(parents=True, exist_ok=True)

    def append(self, title: str, body: str, *, tags: list[str] | None = None, source: str = "manual") -> DurableMemoryEntry:
        created_at = _utc_now()
        tags = tuple(sorted({tag.strip() for tag in tags or [] if str(tag).strip()}))
        entry = DurableMemoryEntry(
            key=_slug(title),
            title=title,
            body=body,
            tags=tags,
            source=source,
            created_at=created_at,
            updated_at=created_at,
        )
        self._write_entry(entry)
        self._append_index(entry)
        return entry

    def search(self, query: str, *, max_results: int = 20, refresh_index: bool = False) -> list[MemorySearchHit]:
        normalized_query = _normalize(query)
        if not normalized_query:
            return []
        keywords = [token for token in re.split(r"\s+", normalized_query) if len(token) > 1][:8]
        if refresh_index:
            self._index_text = None
        index_text = self._read_index_text(refresh_index=refresh_index)
        hits: dict[str, MemorySearchHit] = {}
        for line in index_text.splitlines():
            if not line.startswith("- "):
                continue
            try:
                payload = json.loads(line.split(" ", 1)[1])
            except json.JSONDecodeError:
                continue
            score = _score_entry(payload, keywords)
            if score <= 0:
                continue
            key = payload.get("key")
            hits[key] = MemorySearchHit(
                entry=DurableMemoryEntry(
                    key=payload.get("key", key),
                    title=payload.get("title", ""),
                    body=payload.get("body", ""),
                    tags=tuple(payload.get("tags", [])),
                    source=payload.get("source", ""),
                    created_at=payload.get("created_at", ""),
                    updated_at=payload.get("updated_at", ""),
                ),
                score=score,
                match=_best_excerpt(payload.get("body", ""), keywords),
            )
        return sorted(hits.values(), key=lambda hit: (-hit.score, hit.entry.updated_at))[:max_results]

    def compact(self, keep_recent: int = 40) -> dict[str, object]:
        entries = sorted(self._load_all_entries(), key=lambda entry: (entry.updated_at, entry.created_at, entry.key))
        kept = entries[-keep_recent:] if keep_recent else []
        kept_keys = {entry.key for entry in kept}
        removed = [entry.key for entry in entries[:-keep_recent]] if len(entries) > keep_recent else []
        if not self._index_path.exists():
            self._index_path.write_text("# LoopDesk Memory Index\n\n", encoding="utf-8")
        self._index_path.write_text(
            "".join(self._index_line(entry) for entry in kept), encoding="utf-8"
        )
        self._index_text = None
        for path in sorted(self._memory_dir.glob("memory-*.md")):
            if path.stem.replace("memory-", "") not in kept_keys:
                path.unlink()
        return {
            "kept": len(kept),
            "removed": len(removed),
            "removed_keys": removed,
            "kept_keys": [entry.key for entry in kept],
        }

    def resume_pack(self, max_entries: int = 20) -> dict[str, object]:
        entries = sorted(self._load_all_entries(), key=lambda entry: entry.updated_at)[-max_entries:]
        return {
            "entries": [_serialize_entry(entry) for entry in entries],
            "keywords": sorted({keyword for entry in entries for keyword in entry.tags})[:40],
        }

    def export_state(self, destination: Path | None = None) -> dict[str, object]:
        target = destination or (self._root / "memory" / "resume-pack.json")
        payload = self.resume_pack()
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"path": str(target)}

    def _load_all_entries(self) -> list[DurableMemoryEntry]:
        entries: list[DurableMemoryEntry] = []
        for path in sorted(self._memory_dir.glob("memory-*.md")):
            if path.exists():
                entries.append(_parse_markdown_entry(path))
        return entries

    def _read_index_text(self, *, refresh_index: bool = False) -> str:
        if refresh_index or not hasattr(self, "_index_text") or self._index_text is None:
            self._index_text = self._index_path.read_text(encoding="utf-8") if self._index_path.exists() else ""
        return self._index_text

    def _write_entry(self, entry: DurableMemoryEntry) -> None:
        path = self._memory_dir / f"memory-{entry.key}.md"
        path.write_text(
            "\n".join(
                [
                    f"Title: {entry.title}",
                    f"Source: {entry.source}",
                    f"Tags: {', '.join(entry.tags) or 'none'}",
                    f"Created: {entry.created_at}",
                    f"Updated: {entry.updated_at}",
                    "",
                    entry.body.strip(),
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _append_index(self, entry: DurableMemoryEntry) -> None:
        line = self._index_line(entry)
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._index_path.write_text("# LoopDesk Memory Index\n\n", encoding="utf-8")
        with self._index_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def _index_line(self, entry: DurableMemoryEntry) -> str:
        payload = _serialize_entry(entry)
        return "- {json}\n".format(json=json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _parse_markdown_entry(path: Path) -> DurableMemoryEntry:
    text = path.read_text(encoding="utf-8")
    title = _frontmatter_value(text, "title") or path.stem.replace("memory-", "").replace("-", " ").title()
    tags = tuple(tag.strip() for tag in _frontmatter_value(text, "tags", default="").split(",") if tag.strip())
    created_at = _frontmatter_value(text, "created_at") or _utc_now()
    updated_at = _frontmatter_value(text, "updated_at") or _utc_now()
    body = _parse_markdown_body(text)
    return DurableMemoryEntry(
        key=path.stem.replace("memory-", ""),
        title=title,
        body=body,
        tags=tags,
        source=_frontmatter_value(text, "source", default="manual"),
        created_at=created_at,
        updated_at=updated_at,
    )


def _frontmatter_value(text: str, key: str, *, default: str = "") -> str:
    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def _parse_markdown_body(text: str) -> str:
    if text.startswith("Title:"):
        return text.partition("\n\n")[2].strip()
    return text.split("\n\n", 2)[-1].strip()


def _serialize_entry(entry: DurableMemoryEntry) -> dict[str, Any]:
    return {
        "key": entry.key,
        "title": entry.title,
        "body": entry.body,
        "tags": list(entry.tags),
        "source": entry.source,
        "created_at": entry.created_at,
        "updated_at": entry.updated_at,
    }


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.strip().lower())


def _score_entry(payload: dict[str, Any], keywords: list[str]) -> float:
    haystack = " ".join(
        [
            str(payload.get("title", "")),
            str(payload.get("body", "")),
            ", ".join(payload.get("tags", [])),
        ]
    ).lower()
    return sum(1.0 for keyword in keywords if keyword in haystack)


def _best_excerpt(body: str, keywords: list[str], length: int = 160) -> str:
    text = body.strip()
    if not keywords:
        return text[:length]
    index = min((text.lower().find(keyword) for keyword in keywords if keyword in text.lower()), default=-1)
    if index == -1:
        return text[:length]
    start = max(0, index - 60)
    end = min(len(text), index + length - 60)
    excerpt = text[start:end]
    if start > 0:
        excerpt = "…" + excerpt[1:]
    if end < len(text):
        excerpt = excerpt[:-1] + "…"
    return excerpt


def _slug(title: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return text[:64] or hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
