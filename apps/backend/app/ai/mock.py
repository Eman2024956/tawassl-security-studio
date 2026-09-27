import uuid
from typing import List, Dict, Any
from apps.backend.app.ai.base import BaseAIProvider, AIResponse, ToolCallProposal


class MockProvider(BaseAIProvider):
    """
    Deterministic offline AI Provider for development, testing, and CI.
    Generates reproducible tool call proposals without any external network access.
    """

    async def generate_assessment_plan(
        self,
        target_info: Dict[str, Any],
        profile: str,
        catalog_modules: List[Dict[str, Any]]
    ) -> AIResponse:
        base_urls = target_info.get("base_urls", [])
        primary_url = base_urls[0] if base_urls else "https://staging.acmepay.internal:8443"
        source_path = target_info.get("source_path", "app/auth/tokens.py")

        tool_calls = []

        if profile in ("observe", "controlled_active"):
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"mock-call-{uuid.uuid4().hex[:8]}",
                    tool_name="controlled_http_inspect",
                    arguments={
                        "url": f"{primary_url.rstrip('/')}/login",
                        "method": "GET",
                        "headers": {"Accept": "text/html"}
                    },
                    rationale="Audit HTTP response headers for missing HSTS, CSP, and secure cookie attributes."
                )
            )

        if profile in ("source_review", "observe", "controlled_active"):
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"mock-call-{uuid.uuid4().hex[:8]}",
                    tool_name="ast_syntax_inspector",
                    arguments={
                        "file_path": source_path
                    },
                    rationale="Offline AST syntax check to ensure absence of eval() or unquoted subprocess calls."
                )
            )

        return AIResponse(
            provider="mock",
            model_id=self.model_id,
            content="Formulated deterministic baseline assessment plan based on authorized scope.",
            tool_calls=tool_calls,
            prompt_tokens=150,
            completion_tokens=85,
            total_tokens=235,
            duration_ms=25.0
        )

    async def interpret_evidence(
        self,
        finding_candidate: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> AIResponse:
        title = finding_candidate.get("title", "Observed Anomaly")
        return AIResponse(
            provider="mock",
            model_id=self.model_id,
            content=(
                f"Evidence analysis for '{title}':\n"
                "1. Header inspection confirmed absence of Strict-Transport-Security.\n"
                "2. Cookie 'session_id' lacks 'Secure' and 'SameSite' attributes.\n"
                "Recommendation: Confirm finding as verified with Medium/High severity."
            ),
            tool_calls=[],
            prompt_tokens=200,
            completion_tokens=90,
            total_tokens=290,
            duration_ms=30.0
        )

    async def test_connection(self) -> bool:
        return True
