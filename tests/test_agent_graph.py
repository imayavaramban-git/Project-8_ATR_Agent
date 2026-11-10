import pytest
from agent.graph import ticket_agent_app
from models.ticket import TicketResolutionStatus


def test_order_status_resolution_flow():
    initial_state = {
        "ticket_id": "T-101",
        "customer_id": "C-001",
        "subject": "Track my order ORD-1001",
        "message": "Can you check where my order ORD-1001 is?",
        "gathered_facts": {},
        "actions_taken": [],
        "policy_failures": [],
    }

    result = ticket_agent_app.invoke(initial_state)

    assert result["final_status"] == TicketResolutionStatus.RESOLVED.value
    assert "delivered" in result["final_reply"]
    assert result["policy_passed"] is True


def test_safe_refund_flow():
    initial_state = {
        "ticket_id": "T-102",
        "customer_id": "C-001",
        "subject": "Refund ORD-1001",
        "message": "I would like a refund of $49.99 for ORD-1001 please.",
        "gathered_facts": {},
        "actions_taken": [],
        "policy_failures": [],
    }

    result = ticket_agent_app.invoke(initial_state)

    assert result["final_status"] == TicketResolutionStatus.RESOLVED.value
    assert "successfully processed" in result["final_reply"]
    assert len(result["actions_taken"]) == 1


def test_excessive_refund_escalation_flow():
    # Attempting to refund ORD-1003 ($250, exceeds $100 policy limit)
    initial_state = {
        "ticket_id": "T-103",
        "customer_id": "C-001",
        "subject": "Refund ORD-1003",
        "message": "Please refund $250.00 for order ORD-1003.",
        "gathered_facts": {},
        "actions_taken": [],
        "policy_failures": [],
    }

    result = ticket_agent_app.invoke(initial_state)

    assert result["final_status"] == TicketResolutionStatus.ESCALATED.value
    assert result["policy_passed"] is False
    assert any("exceeds autonomous limit" in fail for fail in result["policy_failures"])
    assert result["escalation_diagnosis"] is not None


def test_unknown_ticket_escalation_flow():
    initial_state = {
        "ticket_id": "T-104",
        "customer_id": "C-999",
        "subject": "Something strange",
        "message": "xyz abc random noise 12345",
        "gathered_facts": {},
        "actions_taken": [],
        "policy_failures": [],
    }

    result = ticket_agent_app.invoke(initial_state)

    assert result["final_status"] == TicketResolutionStatus.ESCALATED.value
    assert result["confidence_score"] < 0.80