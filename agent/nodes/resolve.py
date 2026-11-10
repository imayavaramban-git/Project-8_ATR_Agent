from agent.state import AgentState
from models.ticket import TicketIntent, TicketResolutionStatus
from mcp_servers.order_account_server import process_refund, trigger_password_reset


def resolve_ticket_node(state: AgentState) -> dict:
    """Execute required actions and craft final customer reply."""
    intent = state.get("intent")
    facts = state.get("gathered_facts", {})
    entities = state.get("extracted_entities", {})
    actions_taken = []
    final_reply = ""

    if intent == TicketIntent.ORDER_STATUS.value:
        order = facts["order_status"]["order"]
        final_reply = (
            f"Hello, your order {order['order_id']} is currently '{order['status']}'. "
            f"Items: {', '.join(order['items'])}."
        )

    elif intent == TicketIntent.REFUND_REQUEST.value:
        order = facts["order_status"]["order"]
        amount = entities.get("refund_amount") or order["total_amount"]
        result = process_refund(order["order_id"], amount, "Autonomous resolution")
        actions_taken.append({"action": "process_refund", "result": result})
        final_reply = f"Your refund of ${amount:.2f} for order {order['order_id']} has been successfully processed."

    elif intent == TicketIntent.PASSWORD_RESET.value:
        result = trigger_password_reset(entities["email"])
        actions_taken.append({"action": "trigger_password_reset", "result": result})
        final_reply = f"A password reset link has been dispatched to {entities['email']}."

    elif intent == TicketIntent.GENERAL_QUERY.value:
        docs = facts.get("docs_search", {}).get("results", [])
        if docs:
            top_doc = docs[0]
            final_reply = f"{top_doc['title']}: {top_doc['content']}"
        else:
            final_reply = "Thank you for reaching out. Please consult our knowledge base for more details."

    return {
        "final_status": TicketResolutionStatus.RESOLVED.value,
        "final_reply": final_reply,
        "actions_taken": actions_taken,
        "escalation_diagnosis": None,
    }