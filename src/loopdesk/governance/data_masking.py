from __future__ import annotations

import re

class DataMaskingFilter:
    def __init__(self) -> None:
        # Regex patterns for common secrets
        self.patterns = [
            (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[REDACTED_SECRET]"),
            (re.compile(r"password\s*is\s*([a-zA-Z0-9_\-]+)", re.IGNORECASE), "password is [REDACTED_PASSWORD]"),
            (re.compile(r"api[_-]?key\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", re.IGNORECASE), "api_key: [REDACTED_SECRET]"),
        ]

    def mask(self, text: str) -> str:
        result = text
        for pattern, replacement in self.patterns:
            result = pattern.sub(replacement, result)
        return result
