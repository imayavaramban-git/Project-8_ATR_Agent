from typing import List, Optional
from pydantic import BaseModel, Field


class PolicyCheckResult(BaseModel):
    is_safe: bool = Field(..., description="Whether all safety guardrails passed")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    confidence_threshold: float = Field(default=0.85, description="Minimum confidence required to act autonomously")
    failed_rules: List[str] = Field(default_factory=list, description="List of policy violations")
    reasoning: str = Field(..., description="Audit explanation of policy evaluation")


class ActionPlan(BaseModel):
    intent: str
    target_tool: str
    tool_arguments: dict = Field(default_factory=dict)
    is_irreversible: bool = Field(default=False, description="Flags actions like refunds or password resets")