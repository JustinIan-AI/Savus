from __future__ import annotations

from typing import Dict

class QuotaExceededException(Exception):
    """Raised when project or daily token quota is exceeded."""
    pass

class QuotaGovernor:
    """Tracks token consumption, provides daily/project quota guardrails and kill switch."""
    def __init__(self, daily_token_limit: int = 100_000, project_token_limit: int = 500_000) -> None:
        self.daily_token_limit = daily_token_limit
        self.project_token_limit = project_token_limit
        self.daily_usage = 0
        self.project_usage: Dict[str, int] = {}
        self._tripped_projects: Dict[str, bool] = {}

    def record_consumption(self, project_id: str, agent: str, tokens: int) -> None:
        self.daily_usage += tokens
        self.project_usage[project_id] = self.project_usage.get(project_id, 0) + tokens
        if self.daily_usage >= self.daily_token_limit or self.project_usage[project_id] >= self.project_token_limit:
            self._tripped_projects[project_id] = True

    def can_execute(self, project_id: str, estimated_tokens: int) -> bool:
        if self._tripped_projects.get(project_id, False):
            return False
        if self.daily_usage + estimated_tokens > self.daily_token_limit:
            return False
        if self.project_usage.get(project_id, 0) + estimated_tokens > self.project_token_limit:
            return False
        return True

    def check_and_reserve(self, project_id: str, estimated_tokens: int) -> None:
        if not self.can_execute(project_id, estimated_tokens):
            self._tripped_projects[project_id] = True
            raise QuotaExceededException(f"Token budget exceeded for project {project_id}")

    def is_kill_switch_tripped(self, project_id: str) -> bool:
        return self._tripped_projects.get(project_id, False)
