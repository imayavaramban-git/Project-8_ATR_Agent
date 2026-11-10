from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TicketIntent(str, Enum):
    PASSWORD_RESET = "password_reset"
    ORDER_STATUS = "order_status"
    REFUND_REQUEST = "refund_request"
    ACCESS_REQUEST = "access_request"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class TicketResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class TicketPayload(BaseModel):
    ticket_id: str = Field(..., description="Unique identifier of the support ticket")
    customer_id: str = Field(..., description="ID of the customer raising the ticket")
    subject: str = Field(..., description="Subject line of the ticket")
    message: str = Field(..., description="Customer message body")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom channel metadata")


class HumanEscalationDiagnosis(BaseModel):
    reason: str = Field(..., description="Reason autonomous resolution could not proceed")
    confidence_score: float = Field(..., description="Confidence score that triggered the fallback")
    failed_policies: List[str] = Field(default_factory=list, description="Specific safety policies that failed")
    gathered_facts: Dict[str, Any] = Field(default_factory=dict, description="Facts collected prior to escalation")
    recommended_action: str = Field(..., description="Suggested next steps for the human agent")


class TicketResponse(BaseModel):
    ticket_id: str
    status: TicketResolutionStatus
    response_message: str = Field(..., description="Message returned to the customer or ticketing system")
    escalation_diagnosis: Optional[HumanEscalationDiagnosis] = None
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list, description="List of executed tool actions")