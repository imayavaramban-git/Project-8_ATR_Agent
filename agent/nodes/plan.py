from agent.state import AgentState
from models.ticket import TicketIntent


def plan_resolution_node(state: AgentState) -> dict:
    """Determine tool actions needed based on intent."""
    intent = state.get("intent")
    entities = state.get("extracted_entities", {})
    plan = []

    if intent == TicketIntent.ORDER_STATUS.value:
        plan.append({
            "action": "get_order_status",
            "tool": "get_order_status",
            "args": {"order_id": entities.get("order_id", "")},
            "type": "read",
        })

    elif intent == TicketIntent.REFUND_REQUEST.value:
        plan.append({
            "action": "get_order_status",
            "tool": "get_order_status",
            "args": {"order_id": entities.get("order_id", "")},
            "type": "read",
        })
        plan.append({
            "action": "process_refund",
            "tool": "process_refund",
            "args": {
                "order_id": entities.get("order_id", ""),
                "amount": entities.get("refund_amount", 0.0),
                "reason": state.get("subject", "Customer refund request"),
            },
            "type": "write",
        })

    elif intent == TicketIntent.PASSWORD_RESET.value:
        plan.append({
            "action": "trigger_password_reset",
            "tool": "trigger_password_reset",
            "args": {"email": entities.get("email", "")},
            "type": "write",
        })

    elif intent == TicketIntent.GENERAL_QUERY.value:
        plan.append({
            "action": "search_help_docs",
            "tool": "search_help_docs",
            "args": {"query": entities.get("search_query", state.get("subject", ""))},
            "type": "read",
        })

    return {"current_plan": plan}