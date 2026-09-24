from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Optional

class MemoryTier(str, Enum):
    SHORT_TERM = "short_term"
    PROJECT = "project"
    TEAM = "team"

class ThreeTierMemory:
    """Manages short-term run logs, project memory, and team knowledge base."""
    def __init__(self) -> None:
        self.short_term: List[Dict[str, Any]] = []
        self.project_long_term: List[Dict[str, Any]] = []
        self.team_kb: Dict[str, str] = {}

    def add_short_term(self, run_id: str, content: str) -> None:
        self.short_term.append({"run_id": run_id, "content": content})

    def run_memory_dream(self) -> List[Dict[str, Any]]:
        """Distills short-term operational memories into permanent project insights & rules."""
        if not self.short_term:
            return []

        # Extract meaningful patterns, warnings, and error insights from run logs
        extracted_rules = []
        for item in self.short_term:
            text = item.get("content", "")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for line in lines:
                if any(kw in line.lower() for kw in ["error", "fail", "rule", "gate", "reject", "warning"]):
                    extracted_rules.append(line)

        summary_content = "\n".join(extracted_rules) if extracted_rules else "\n".join([item["content"] for item in self.short_term])
        distilled_record = {
            "distilled_knowledge": summary_content,
            "source_runs_count": len(self.short_term),
            "key_rules_extracted": extracted_rules[:10]
        }
        self.project_long_term.append(distilled_record)
        self.short_term.clear()
        return [distilled_record]

    def get_long_term_count(self) -> int:
        return len(self.project_long_term)

    def store(self, tier: MemoryTier, key: str, text: str) -> None:
        if tier == MemoryTier.TEAM:
            self.team_kb[key] = text
        elif tier == MemoryTier.PROJECT:
            self.project_long_term.append({"key": key, "content": text})

    def retrieve(self, query: str, tier: MemoryTier) -> List[str]:
        q = query.lower()
        if tier == MemoryTier.TEAM:
            return [v for k, v in self.team_kb.items() if q in v.lower() or q in k.lower()]
        elif tier == MemoryTier.PROJECT:
            results = []
            for item in self.project_long_term:
                c = item.get("content", item.get("distilled_knowledge", ""))
                k = item.get("key", "")
                if q in c.lower() or q in k.lower():
                    results.append(c)
            return results
        elif tier == MemoryTier.SHORT_TERM:
            return [item["content"] for item in self.short_term if q in item.get("content", "").lower()]
        return []
