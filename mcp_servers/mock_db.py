"""
In-memory mock database representing company systems (CRM, Orders, Knowledge Base).
"""
from typing import Dict, Any, Optional

ORDERS_DB: Dict[str, Dict[str, Any]] = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "status": "delivered",
        "total_amount": 49.99,
        "items": ["Wireless Mouse", "USB-C Cable"],
        "delivered_at": "2026-10-15T10:30:00Z",
        "refund_status": None,
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUST-002",
        "status": "in_transit",
        "total_amount": 120.00,
        "items": ["Mechanical Keyboard"],
        "delivered_at": None,
        "refund_status": None,
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUST-001",
        "status": "processing",
        "total_amount": 250.00,
        "items": ["27-inch Monitor"],
        "delivered_at": None,
        "refund_status": None,
    },
}

USERS_DB: Dict[str, Dict[str, Any]] = {
    "user1@example.com": {
        "user_id": "CUST-001",
        "email": "user1@example.com",
        "name": "Jane Doe",
        "status": "active",
        "reset_token_sent": False,
    },
    "user2@example.com": {
        "user_id": "CUST-002",
        "email": "user2@example.com",
        "name": "John Smith",
        "status": "locked",
        "reset_token_sent": False,
    },
}

KNOWLEDGE_BASE: list[Dict[str, str]] = [
    {
        "doc_id": "DOC-01",
        "title": "Refund Policy",
        "content": "Refunds are eligible within 30 days of delivery. Orders above $100 require human review. Processing orders cannot be refunded immediately without cancellation.",
    },
    {
        "doc_id": "DOC-02",
        "title": "Password Reset Procedures",
        "content": "Users can request a password reset link sent to their primary verified email. Suspended or locked accounts require manual identity verification.",
    },
    {
        "doc_id": "DOC-03",
        "title": "Access Request Guidelines",
        "content": "Access requests for internal tools (GitHub, AWS, Looker) require approval from the engineering team lead.",
    },
]