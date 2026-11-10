from agent.state import AgentState
from models.ticket import TicketIntent

CONFIDENCE_THRESHOLD = 0.80
MAX_AUTONOMOUS_REFUND = 100.00


def guardrail_check_node(state: AgentState) -> dict:
    """Evaluate policies and confidence before executing irreversible actions."""
    failures = []
    confidence = state.get("confidence_score", 0.0)

    # 1. Confidence threshold check
    if confidence < CONFIDENCE_THRESHOLD:
        failures.append(f"Confidence score {confidence:.2f} is below required {CONFIDENCE_THRESHOLD}")

    intent = state.get("intent")
    facts = state.get("gathered_facts", {})
    entities = state.get("extracted_entities", {})

    # 2. Refund policy guardrails
    if intent == TicketIntent.REFUND_REQUEST.value:
        order_info = facts.get("order_status", {})
        if not order_info.get("found"):
            failures.append("Target order not found in company records.")
        else:
            order = order_info["order"]
            if order.get("status") != "delivered":
                failures.append(f"Order status is '{order.get('status')}'. Must be 'delivered' for refund.")
            
            amount = entities.get("refund_amount") or order.get("total_amount", 0.0)
            if amount > MAX_AUTONOMOUS_REFUND:
                failures.append(f"Refund amount ${amount:.2f} exceeds autonomous limit of ${MAX_AUTONOMOUS_REFUND:.2f}.")

    # 3. Password reset guardrails
    elif intent == TicketIntent.PASSWORD_RESET.value:
        if not entities.get("email"):
            failures.append("No valid email address found in ticket.")

    is_safe = len(failures) == 0

    return {
        "policy_passed": is_safe,
        "policy_failures": failures,
    }