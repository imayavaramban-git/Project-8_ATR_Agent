import pytest
from mcp_servers.order_account_server import (
    get_order_status,
    process_refund,
    trigger_password_reset,
)
from mcp_servers.knowledge_server import search_help_docs
from mcp_servers.mock_db import ORDERS_DB, USERS_DB


def test_get_order_status_found():
    result = get_order_status("ORD-1001")
    assert result["found"] is True
    assert result["order"]["status"] == "delivered"


def test_get_order_status_not_found():
    result = get_order_status("ORD-9999")
    assert result["found"] is False


def test_process_refund_success():
    result = process_refund("ORD-1001", amount=49.99, reason="Customer not satisfied")
    assert result["success"] is True
    assert ORDERS_DB["ORD-1001"]["refund_status"] == "processed"


def test_process_refund_undelivered_order():
    # ORD-1002 is 'in_transit'
    result = process_refund("ORD-1002", amount=50.0, reason="Item late")
    assert result["success"] is False
    assert "Cannot refund" in result["message"]


def test_process_refund_excessive_amount():
    # ORD-1001 total amount is 49.99
    result = process_refund("ORD-1001", amount=500.0, reason="Excessive")
    assert result["success"] is False
    assert "exceeds order total" in result["message"]


def test_password_reset_success():
    result = trigger_password_reset("user1@example.com")
    assert result["success"] is True
    assert USERS_DB["user1@example.com"]["reset_token_sent"] is True


def test_password_reset_locked_account():
    # user2@example.com is locked
    result = trigger_password_reset("user2@example.com")
    assert result["success"] is False
    assert "Account is locked" in result["message"]


def test_search_help_docs():
    result = search_help_docs("refund policy")
    assert result["matches_count"] >= 1
    assert any(doc["doc_id"] == "DOC-01" for doc in result["results"])