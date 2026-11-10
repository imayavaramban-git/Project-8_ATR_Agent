from agent.state import AgentState
from agent.prompts import extract_ticket_intent_heuristic


def understand_ticket_node(state: AgentState) -> dict:
    """Classify ticket intent and extract key entities."""
    extracted = extract_ticket_intent_heuristic(state["subject"], state["message"])

    entities = {}
    if extracted.order_id:
        entities["order_id"] = extracted.order_id
    if extracted.email:
        entities["email"] = extracted.email
    if extracted.refund_amount:
        entities["refund_amount"] = extracted.refund_amount
    if extracted.search_query:
        entities["search_query"] = extracted.search_query

    return {
        "intent": extracted.intent.value,
        "extracted_entities": entities,
        "confidence_score": extracted.confidence_score,
    }