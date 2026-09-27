from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str


class TargetCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=2, max_length=100)
    target_type: str = Field(..., pattern="^(website|api|source|combined)$")
    environment_mode: str = Field("live", pattern="^(live|mock)$")
    authorized_domains: List[str]
    base_urls: List[str]
    allowed_ports: Optional[List[int]] = [80, 443]
    allow_subdomains: bool = False
    exclusions: Optional[List[str]] = []
    source_path: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None


class TargetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    target_type: str
    environment_mode: str = "live"
    authorized_domains: List[str]
    base_urls: List[str]
    allowed_ports: List[int]
    allow_subdomains: bool
    exclusions: List[str]
    source_path: Optional[str]
    created_at: str


class AssessmentCreate(BaseModel):
    project_id: str
    target_id: str
    name: str = Field(..., min_length=2, max_length=100)
    profile: str = Field(..., pattern="^(observe|source_review|controlled_active|authenticated|regression)$")
    ai_provider: Optional[str] = "mock"
    model_id: Optional[str] = "mock-sec-v1"
    max_steps: Optional[int] = 20
    max_requests: Optional[int] = 50
    max_tool_calls: Optional[int] = 30
    timeout_seconds: Optional[int] = 300
    max_output_bytes: Optional[int] = 2 * 1024 * 1024


class AssessmentResponse(BaseModel):
    id: str
    project_id: str
    target_id: str
    name: str
    profile: str
    status: str
    ai_provider: str
    model_id: str
    max_steps: int
    max_requests: int
    max_tool_calls: int
    timeout_seconds: int
    max_output_bytes: int
    steps_taken: int
    requests_made: int
    tool_calls_made: int
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    created_at: str


class ProposalDecision(BaseModel):
    decision: str = Field(..., pattern="^(approve|reject|stop)$")
    reason: Optional[str] = None


class ProposalResponse(BaseModel):
    id: str
    assessment_id: str
    tool_name: str
    arguments: Dict[str, Any]
    arguments_hash: str
    purpose: str
    side_effects: str
    resource_limits: Dict[str, Any]
    status: str
    approved_by: Optional[str]
    approved_at: Optional[str]
    consumed_at: Optional[str]
    created_at: str


class FindingResponse(BaseModel):
    id: str
    assessment_id: str
    title: str
    category: str
    affected_asset: str
    severity: str  # critical, high, medium, low, info
    confidence: str  # confirmed, high, medium, low
    status: str  # observation, suspected, confirmed, inconclusive, false_positive, fixed, retest_failed
    result_type: str = "finding"  # passed_control, observation, finding, inconclusive
    confirmed_vulnerability: bool = False
    evidence_hash: Optional[str] = None
    preconditions: Optional[str] = None
    reproduction_steps: str
    expected_result: str
    observed_result: str
    impact: Optional[str] = None
    remediation: Optional[str] = None
    evidence: List[Dict[str, Any]]
    created_at: str
    updated_at: str

