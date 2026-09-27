from typing import Optional
from apps.backend.app.core.config import settings
from apps.backend.app.ai.base import BaseAIProvider
from apps.backend.app.ai.mock import MockProvider
from apps.backend.app.ai.gemini import GeminiProvider
from apps.backend.app.ai.openai import OpenAIProvider


def get_ai_provider(provider_name: Optional[str] = None, model_id: Optional[str] = None) -> BaseAIProvider:
    """Factory to retrieve configured AI provider. Falls back safely to MockProvider if keys are absent."""
    name = (provider_name or settings.DEFAULT_AI_PROVIDER).lower()

    if name == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiProvider(
                model_id=model_id or "gemini-2.5-flash",
                api_key=settings.GEMINI_API_KEY,
                timeout_seconds=float(settings.DEFAULT_TIMEOUT_SECONDS)
            )
        # Fall back to MockProvider if Gemini requested but key omitted
        return MockProvider(model_id=model_id or "mock-gemini-fallback")

    if name == "openai":
        if settings.OPENAI_API_KEY:
            return OpenAIProvider(
                model_id=model_id or "gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                timeout_seconds=float(settings.DEFAULT_TIMEOUT_SECONDS)
            )
        # Fall back to MockProvider if OpenAI requested but key omitted
        return MockProvider(model_id=model_id or "mock-openai-fallback")

    # Default: MockProvider
    return MockProvider(model_id=model_id or settings.DEFAULT_MODEL_ID)
