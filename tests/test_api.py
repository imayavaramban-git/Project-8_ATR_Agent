import pytest
from fastapi.testclient import TestClient
from api.main import app
from models.ticket import TicketResolutionStatus

client = TestClient(app)


def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "resolve-ai"}


def test_resolve_order_status_endpoint():
    payload = {
        "ticket_id": "T-API-001",
        "customer_id": "C-100",
        "subject": "Status check on ORD-1001",
        "message": "When will my order ORD-1001 arrive?",
        "metadata": {"source": "mobile_app"},
    }
    response = client.post("/tickets/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "T-API-001"
    assert data["status"] == TicketResolutionStatus.RESOLVED.value
    assert "delivered" in data["response_message"]
    assert data["escalation_diagnosis"] is None


def test_resolve_refund_escalation_endpoint():
    # Ticket requesting refund on ORD-1003 ($250, violates <= $100 policy)
    payload = {
        "ticket_id": "T-API-002",
        "customer_id": "C-200",
        "subject": "Refund ORD-1003",
        "message": "Please refund $250 for order ORD-1003.",
        "metadata": {},
    }
    response = client.post("/tickets/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "T-API-002"
    assert data["status"] == TicketResolutionStatus.ESCALATED.value
    assert data["escalation_diagnosis"] is not None
    assert any("exceeds autonomous limit" in fail for fail in data["escalation_diagnosis"]["failed_policies"])


def test_invalid_ticket_payload_validation():
    # Payload missing required 'subject' and 'message' fields
    payload = {
        "ticket_id": "T-API-003",
        "customer_id": "C-300",
    }
    response = client.post("/tickets/resolve", json=payload)
    assert response.status_code == 422