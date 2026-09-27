from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolCallProposal(BaseModel):
    call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    rationale: Optional[str] = None


class AIResponse(BaseModel):
    provider: str
    model_id: str
    content: Optional[str] = None
    tool_calls: List[ToolCallProposal] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: float = 0.0


class BaseAIProvider(ABC):
    """Abstract base adapter for AI providers."""

    def __init__(self, model_id: str, api_key: Optional[str] = None, timeout_seconds: float = 30.0):
        self.model_id = model_id
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def generate_assessment_plan(
        self,
        target_info: Dict[str, Any],
        profile: str,
        catalog_modules: List[Dict[str, Any]]
    ) -> AIResponse:
        """Plans assessment steps without executing any actions."""
        pass

    @abstractmethod
    async def interpret_evidence(
        self,
        finding_candidate: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> AIResponse:
        """Interprets raw evidence and proposes verification verdict."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Tests API connectivity with backend credentials."""
        pass
