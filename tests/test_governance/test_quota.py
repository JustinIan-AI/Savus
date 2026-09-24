from __future__ import annotations

import pytest
from loopdesk.governance.quota import QuotaGovernor, QuotaExceededException

def test_quota_limits_and_kill_switch():
    governor = QuotaGovernor(daily_token_limit=100_000, project_token_limit=500_000)

    # Record normal usage
    governor.record_consumption(project_id="proj-1", agent="claude-code", tokens=40_000)
    assert governor.can_execute(project_id="proj-1", estimated_tokens=10_000) is True

    # Consume up to daily limit
    governor.record_consumption(project_id="proj-1", agent="claude-code", tokens=60_000)

    # Now daily limit is 100_000, requesting more should trigger kill switch
    with pytest.raises(QuotaExceededException) as exc:
        governor.check_and_reserve(project_id="proj-1", estimated_tokens=5_000)
    assert "budget exceeded" in str(exc.value).lower()

    assert governor.is_kill_switch_tripped(project_id="proj-1") is True
