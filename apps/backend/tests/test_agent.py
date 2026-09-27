import pytest
from apps.backend.app.agent.budgets import BudgetTracker, BudgetExhaustedError
from apps.backend.app.agent.orchestrator import AssessmentOrchestrator
from apps.backend.app.policy.models import ScopeRule
from apps.backend.app.ai.mock import MockProvider
from apps.backend.app.core.config import settings
from apps.backend.app.core.database import init_db


def test_budget_step_exhaustion():
    tracker = BudgetTracker(max_steps=2)
    tracker.record_step()
    tracker.record_step()
    assert tracker.steps_taken == 2

    # Exceeding step budget must raise BudgetExhaustedError
    with pytest.raises(BudgetExhaustedError) as exc_info:
        tracker.record_step()
    assert "steps" in str(exc_info.value)


def test_budget_request_exhaustion():
    tracker = BudgetTracker(max_requests=5)
    tracker.record_request(3)
    assert tracker.requests_made == 3

    # Exceeding request budget
    with pytest.raises(BudgetExhaustedError) as exc_info:
        tracker.record_request(3)  # 3 + 3 = 6 > 5
    assert "requests" in str(exc_info.value)


@pytest.mark.asyncio
async def test_orchestrator_step_flow():
    await init_db()

    scope = ScopeRule(
        authorized_domains=["staging.acmepay.internal"],
        base_urls=["https://staging.acmepay.internal:8443"],
        source_root="/workspace"
    )
    budgets = BudgetTracker(max_steps=5, max_requests=10)
    provider = MockProvider(model_id="mock-test")

    orchestrator = AssessmentOrchestrator(
        assessment_id="test-assess-1",
        target_info={
            "target_type": "website",
            "authorized_domains": ["staging.acmepay.internal"],
            "base_urls": ["https://staging.acmepay.internal:8443"],
            "source_path": "app/tokens.py"
        },
        scope_rule=scope,
        profile="observe",
        ai_provider=provider,
        budget_tracker=budgets,
        db_path=str(settings.DATABASE_PATH)
    )

    result = await orchestrator.execute_step()
    assert result["step"] == 1
    assert "results" in result
    assert result["budgets"]["steps_taken"] == 1
