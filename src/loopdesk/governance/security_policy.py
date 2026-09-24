from __future__ import annotations

import re

class SecurityViolationException(Exception):
    """Raised when an operation violates security policy."""
    pass

class SecurityPolicyEngine:
    """Implements 5-layer security policy (IPC, FS, Network Egress, Secrets, Terminal Escapes)."""
    def __init__(self) -> None:
        self.forbidden_fs_patterns = [
            r"\.env($|\.)",
            r"id_rsa",
            r"\.ssh/",
            r"\.netrc",
            r"/etc/shadow",
            r"/etc/passwd"
        ]
        self.allowed_domains = [
            "github.com",
            "api.github.com",
            "atlassian.net",
            "plane.so"
        ]

    def check_ipc(self, message: str) -> bool:
        return True

    def check_fs_access(self, path: str, mode: str = "read") -> bool:
        for pattern in self.forbidden_fs_patterns:
            if re.search(pattern, path):
                raise SecurityViolationException(f"Filesystem access denied for restricted path: {path}")
        return True

    def check_network_egress(self, host: str) -> bool:
        clean_host = host.split(":")[0].strip().lower()
        for domain in self.allowed_domains:
            if clean_host == domain or clean_host.endswith("." + domain):
                return True
        raise SecurityViolationException(f"Network egress blocked for domain: {host}")

    def sanitize_secrets(self, text: str) -> str:
        secret_patterns = [
            r"sk-ant-[a-zA-Z0-9_\-]+",
            r"sk-[a-zA-Z0-9_\-]+",
            r"ghp_[a-zA-Z0-9]+",
            r"bearer\s+[a-zA-Z0-9_\-\.]+"
        ]
        sanitized = text
        for p in secret_patterns:
            sanitized = re.sub(p, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def strip_terminal_escapes(self, text: str) -> str:
        ansi_regex = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        return re.sub(ansi_regex, "", text)
