from __future__ import annotations

import pytest
from loopdesk.governance.budget_guard import BudgetGuard, QuotaExceededException
from loopdesk.governance.data_masking import DataMaskingFilter

def test_token_budget_quota_and_circuit_breaker():
    guard = BudgetGuard(max_tokens_per_project=1000, warning_threshold=0.8)

    # Normal usage
    guard.record_usage("project-a", tokens=500)
    assert guard.is_warning("project-a") is False
    assert guard.can_proceed("project-a") is True

    # Near limit -> warning
    guard.record_usage("project-a", tokens=350) # total 850 >= 800
    assert guard.is_warning("project-a") is True
    assert guard.can_proceed("project-a") is True

    # Exceeded -> breaker trips
    with pytest.raises(QuotaExceededException):
        guard.record_usage("project-a", tokens=200) # total 1050 > 1000

    assert guard.can_proceed("project-a") is False

def test_data_masking_filter():
    filter_engine = DataMaskingFilter()
    
    raw_prompt = "Here is my secret token: ghp_1234567890abcdefghijklmnopqrstuvwxyz and my password is SecretPassword123"
    masked = filter_engine.mask(raw_prompt)
    
    assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in masked
    assert "[REDACTED_SECRET]" in masked
    assert "[REDACTED_SECRET]" in masked or "[REDACTED_PASSWORD]" in masked
