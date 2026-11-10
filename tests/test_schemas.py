# tests/test_schemas.py
import pytest
from pydantic import ValidationError

from models.ticket import (
    TicketPayload,
    TicketResponse,
    TicketIntent,
    TicketResolutionStatus,
    HumanEscalationDiagnosis,
)
from models.decision import PolicyCheckResult, ActionPlan
from agent.state import AgentState


def test_ticket_payload_valid():
    payload = TicketPayload(
        ticket_id="TICK-101",
        customer_id="CUST-456",
        subject="Order issue",
        message="My package has not arrived.",
        metadata={"channel": "web"},
    )
    assert payload.ticket_id == "TICK-101"
    assert payload.customer_id == "CUST-456"
    assert payload.metadata["channel"] == "web"


def test_ticket_payload_missing_required_fields():
    with pytest.raises(ValidationError):
        # Missing required fields like ticket_id, customer_id, subject, message
        TicketPayload(ticket_id="TICK-102")


def test_policy_check_confidence_range():
    # Valid confidence score between 0.0 and 1.0
    valid_check = PolicyCheckResult(
        is_safe=True,
        confidence_score=0.92,
        reasoning="All policies satisfied",
    )
    assert valid_check.confidence_score == 0.92

    # Confidence score exceeding 1.0 must fail validation
    with pytest.raises(ValidationError):
        PolicyCheckResult(
            is_safe=True,
            confidence_score=1.5,
            reasoning="Invalid score",
        )

    # Negative confidence score must fail validation
    with pytest.raises(ValidationError):
        PolicyCheckResult(
            is_safe=False,
            confidence_score=-0.1,
            reasoning="Invalid score",
        )


def test_ticket_response_with_escalation():
    diagnosis = HumanEscalationDiagnosis(
        reason="Confidence score below policy threshold",
        confidence_score=0.62,
        failed_policies=["min_confidence_check"],
        gathered_facts={"order_status": "delayed"},
        recommended_action="Manually check carrier tracking",
    )

    response = TicketResponse(
        ticket_id="TICK-101",
        status=TicketResolutionStatus.ESCALATED,
        response_message="Your ticket has been escalated to human support.",
        escalation_diagnosis=diagnosis,
        actions_taken=[],
    )

    assert response.status == TicketResolutionStatus.ESCALATED
    assert response.escalation_diagnosis is not None
    assert response.escalation_diagnosis.confidence_score == 0.62


def test_agent_state_instantiation():
    state: AgentState = {
        "ticket_id": "TICK-101",
        "customer_id": "CUST-456",
        "subject": "Reset my password",
        "message": "I lost access to my corporate email.",
        "intent": TicketIntent.PASSWORD_RESET.value,
        "extracted_entities": {"email": "user@example.com"},
        "current_plan": [{"step": 1, "action": "verify_user"}],
        "gathered_facts": {"user_active": True},
        "actions_taken": [],
        "confidence_score": 0.95,
        "policy_passed": True,
        "policy_failures": [],
        "final_status": TicketResolutionStatus.RESOLVED.value,
        "final_reply": "Password reset instructions have been dispatched.",
        "escalation_diagnosis": None,
    }

    assert state["intent"] == "password_reset"
    assert state["confidence_score"] == 0.95