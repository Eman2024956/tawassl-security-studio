import pytest
from apps.backend.app.ai.mock import MockProvider
from apps.backend.app.ai.factory import get_ai_provider


@pytest.mark.asyncio
async def test_mock_provider_plan_generation():
    provider = MockProvider(model_id="mock-sec-v1")
    target_info = {
        "target_type": "website",
        "authorized_domains": ["staging.acmepay.internal"],
        "base_urls": ["https://staging.acmepay.internal:8443"],
        "source_path": "app/tokens.py"
    }

    res = await provider.generate_assessment_plan(
        target_info=target_info,
        profile="observe",
        catalog_modules=[]
    )

    assert res.provider == "mock"
    assert len(res.tool_calls) >= 1
    # Check that tool call is typed and has arguments
    first_call = res.tool_calls[0]
    assert first_call.tool_name in ("controlled_http_inspect", "ast_syntax_inspector")
    assert "url" in first_call.arguments or "file_path" in first_call.arguments


@pytest.mark.asyncio
async def test_mock_provider_evidence_interpretation():
    provider = MockProvider(model_id="mock-sec-v1")
    finding = {"title": "Missing HSTS Header"}
    evidence = [{"type": "http_response", "content": "HTTP/1.1 200 OK\r\nServer: nginx"}]

    res = await provider.interpret_evidence(finding, evidence)
    assert res.provider == "mock"
    assert "HSTS" in res.content
    assert res.duration_ms > 0


def test_ai_factory_fallback_behavior():
    # When keys are not set, factory falls back to MockProvider
    provider_gemini = get_ai_provider("gemini")
    assert isinstance(provider_gemini, MockProvider)

    provider_openai = get_ai_provider("openai")
    assert isinstance(provider_openai, MockProvider)

    provider_mock = get_ai_provider("mock")
    assert isinstance(provider_mock, MockProvider)
