from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ScopeRule(BaseModel):
    authorized_domains: List[str] = Field(default_factory=list)
    base_urls: List[str] = Field(default_factory=list)
    allowed_ports: List[int] = Field(default_factory=lambda: [80, 443])
    allow_subdomains: bool = False
    exclusions: List[str] = Field(default_factory=list)
    source_root: Optional[str] = None


class PolicyEvaluationResult(BaseModel):
    allowed: bool
    reason: str
    resolved_ip: Optional[str] = None
    canonical_target: Optional[str] = None
    violation_code: Optional[str] = None
