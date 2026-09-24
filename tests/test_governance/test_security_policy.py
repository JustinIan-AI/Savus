from __future__ import annotations

import pytest
from loopdesk.governance.security_policy import SecurityPolicyEngine, SecurityViolationException

def test_five_layer_security():
    engine = SecurityPolicyEngine()

    # Layer 1: IPC check
    assert engine.check_ipc("safe_message") is True

    # Layer 2: Filesystem protection (.env or private key must be blocked)
    with pytest.raises(SecurityViolationException) as exc_fs:
        engine.check_fs_access(path=".env", mode="write")
    assert "access denied" in str(exc_fs.value).lower()

    with pytest.raises(SecurityViolationException) as exc_key:
        engine.check_fs_access(path="/home/user/.ssh/id_rsa", mode="read")
    assert "access denied" in str(exc_key.value).lower()

    # Allowed fs access
    assert engine.check_fs_access(path="src/main.py", mode="write") is True

    # Layer 3: Network domain egress
    with pytest.raises(SecurityViolationException) as exc_net:
        engine.check_network_egress(host="malicious-exfiltration.com")
    assert "egress blocked" in str(exc_net.value).lower()

    assert engine.check_network_egress(host="api.github.com") is True

    # Layer 4: Secret redaction
    cleaned_text = engine.sanitize_secrets("Authorization: Bearer sk-ant-api03-abcdef1234567890")
    assert "sk-ant-" not in cleaned_text
    assert "[REDACTED]" in cleaned_text

    # Layer 5: Terminal escape sequences strip
    raw_ansi = "\x1b[31mError\x1b[0m occurred"
    assert engine.strip_terminal_escapes(raw_ansi) == "Error occurred"
