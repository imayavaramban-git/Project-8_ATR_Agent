"""
Prompt templates and entity extraction parsing for ticket analysis.
"""
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from models.ticket import TicketIntent


class ExtractedTicketData(BaseModel):
    intent: TicketIntent
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    order_id: Optional[str] = None
    email: Optional[str] = None
    refund_amount: Optional[float] = None
    search_query: Optional[str] = None


def extract_ticket_intent_heuristic(subject: str, message: str) -> ExtractedTicketData:
    """
    Deterministic rule-based extractor (used as baseline/fallback to keep evals reproducible).
    """
    text = f"{subject} {message}".lower()

    # Order ID regex (matches ORD-xxxx)
    order_match = re.search(r"\b(ord-\d+)\b", text, re.IGNORECASE)
    order_id = order_match.group(1).upper() if order_match else None

    # Email regex
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    email = email_match.group(0).lower() if email_match else None

    # Refund amount regex (e.g. $49.99, 50 dollars)
    amount_match = re.search(r"\$(\d+(?:\.\d{1,2})?)", text)
    refund_amount = float(amount_match.group(1)) if amount_match else None

    # Intent routing
    if "refund" in text or "money back" in text:
        confidence = 0.95 if order_id else 0.60
        return ExtractedTicketData(
            intent=TicketIntent.REFUND_REQUEST,
            confidence_score=confidence,
            order_id=order_id,
            refund_amount=refund_amount,
        )

    if "password" in text or "reset" in text or "locked out" in text:
        confidence = 0.95 if email else 0.60
        return ExtractedTicketData(
            intent=TicketIntent.PASSWORD_RESET,
            confidence_score=confidence,
            email=email,
        )

    if "order" in text or "track" in text or "status" in text or "package" in text:
        confidence = 0.95 if order_id else 0.60
        return ExtractedTicketData(
            intent=TicketIntent.ORDER_STATUS,
            confidence_score=confidence,
            order_id=order_id,
        )

    if "how to" in text or "policy" in text or "help" in text:
        return ExtractedTicketData(
            intent=TicketIntent.GENERAL_QUERY,
            confidence_score=0.90,
            search_query=subject or message,
        )

    return ExtractedTicketData(
        intent=TicketIntent.UNKNOWN,
        confidence_score=0.30,
    )