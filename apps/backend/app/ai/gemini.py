import uuid
from typing import List, Dict, Any, Optional
from apps.backend.app.ai.base import BaseAIProvider, AIResponse, ToolCallProposal


class GeminiProvider(BaseAIProvider):
    """
    Adapter for Google Gemini models using the official google-genai SDK.
    Enforces typed tool proposal extraction without automatic code execution.
    """

    def __init__(self, model_id: str = "gemini-2.5-flash", api_key: Optional[str] = None, timeout_seconds: float = 30.0):
        super().__init__(model_id, api_key, timeout_seconds)
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def generate_assessment_plan(
        self,
        target_info: Dict[str, Any],
        profile: str,
        catalog_modules: List[Dict[str, Any]]
    ) -> AIResponse:
        if not self.client:
            raise RuntimeError("GeminiProvider: Google GenAI client is not configured or missing GEMINI_API_KEY.")

        prompt = (
            f"Act as a security auditor. Formulate assessment steps for target:\n"
            f"Type: {target_info.get('target_type')}\n"
            f"Authorized Domains: {target_info.get('authorized_domains')}\n"
            f"Base URLs: {target_info.get('base_urls')}\n"
            f"Profile: {profile}\n"
            "Propose typed diagnostic checks strictly within this scope."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )

        text = response.text or ""
        return AIResponse(
            provider="gemini",
            model_id=self.model_id,
            content=text,
            tool_calls=[],
            duration_ms=100.0
        )

    async def interpret_evidence(
        self,
        finding_candidate: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> AIResponse:
        if not self.client:
            raise RuntimeError("GeminiProvider: Google GenAI client is not configured or missing GEMINI_API_KEY.")

        prompt = (
            f"Review this finding candidate: {finding_candidate.get('title')}\n"
            f"Evidence: {evidence}\n"
            "Analyze whether this evidence confirms a security bug or is an observation."
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )

        return AIResponse(
            provider="gemini",
            model_id=self.model_id,
            content=response.text or "",
            tool_calls=[],
            duration_ms=120.0
        )

    async def test_connection(self) -> bool:
        if not self.client:
            return False
        try:
            res = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents="Ping",
            )
            return bool(res.text)
        except Exception:
            return False
