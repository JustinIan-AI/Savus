from __future__ import annotations

class QuotaExceededException(Exception):
    pass

class BudgetGuard:
    def __init__(self, max_tokens_per_project: int = 100000, warning_threshold: float = 0.8) -> None:
        self.max_tokens = max_tokens_per_project
        self.warning_threshold = warning_threshold
        self._usage: dict[str, int] = {}

    def record_usage(self, project_id: str, tokens: int) -> None:
        current = self._usage.get(project_id, 0)
        new_total = current + tokens
        if new_total > self.max_tokens:
            self._usage[project_id] = new_total
            raise QuotaExceededException(f"Project {project_id} token quota exceeded: {new_total} > {self.max_tokens}")
        self._usage[project_id] = new_total

    def is_warning(self, project_id: str) -> bool:
        current = self._usage.get(project_id, 0)
        return (current / self.max_tokens) >= self.warning_threshold

    def can_proceed(self, project_id: str) -> bool:
        current = self._usage.get(project_id, 0)
        return current <= self.max_tokens
