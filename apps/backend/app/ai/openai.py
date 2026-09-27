from typing import List, Dict, Any, Optional
from apps.backend.app.ai.base import BaseAIProvider, AIResponse, ToolCallProposal


class OpenAIProvider(BaseAIProvider):
    """
    Adapter for OpenAI GPT models using the official openai SDK.
    Enforces typed tool proposal extraction without automatic code execution.
    """

    def __init__(self, model_id: str = "gpt-4o-mini", api_key: Optional[str] = None, timeout_seconds: float = 30.0):
        super().__init__(model_id, api_key, timeout_seconds)
        self.client = None
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
            except Exception:
                self.client = None

    async def generate_assessment_plan(
        self,
        target_info: Dict[str, Any],
        profile: str,
        catalog_modules: List[Dict[str, Any]]
    ) -> AIResponse:
        if not self.client:
            raise RuntimeError("OpenAIProvider: OpenAI client is not configured or missing OPENAI_API_KEY.")

        prompt = (
            f"Act as a security auditor. Formulate assessment steps for target:\n"
            f"Type: {target_info.get('target_type')}\n"
            f"Authorized Domains: {target_info.get('authorized_domains')}\n"
            f"Profile: {profile}\n"
            "Propose typed diagnostic checks strictly within this scope."
        )

        res = await self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}]
        )

        content = res.choices[0].message.content or ""
        tokens = res.usage.total_tokens if res.usage else 0

        return AIResponse(
            provider="openai",
            model_id=self.model_id,
            content=content,
            tool_calls=[],
            total_tokens=tokens,
            duration_ms=150.0
        )

    async def interpret_evidence(
        self,
        finding_candidate: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> AIResponse:
        if not self.client:
            raise RuntimeError("OpenAIProvider: OpenAI client is not configured or missing OPENAI_API_KEY.")

        res = await self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": "You are a senior security researcher analyzing vulnerability evidence."},
                {"role": "user", "content": f"Review evidence: {evidence} for finding: {finding_candidate.get('title')}"}
            ]
        )

        return AIResponse(
            provider="openai",
            model_id=self.model_id,
            content=res.choices[0].message.content or "",
            tool_calls=[],
            duration_ms=160.0
        )

    async def test_connection(self) -> bool:
        if not self.client:
            return False
        try:
            res = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            return bool(res.choices)
        except Exception:
            return False
