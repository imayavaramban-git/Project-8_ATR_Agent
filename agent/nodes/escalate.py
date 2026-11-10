from agent.state import AgentState
from models.ticket import TicketResolutionStatus


def escalate_ticket_node(state: AgentState) -> dict:
    """Construct an escalation report for human agents."""
    diagnosis = {
        "reason": "Autonomous guardrail check failed.",
        "confidence_score": state.get("confidence_score", 0.0),
        "failed_policies": state.get("policy_failures", []),
        "gathered_facts": state.get("gathered_facts", {}),
        "recommended_action": "Review ticket manually and verify identity or order parameters.",
    }

    return {
        "final_status": TicketResolutionStatus.ESCALATED.value,
        "final_reply": "Your request has been routed to a human support specialist for review.",
        "escalation_diagnosis": diagnosis,
    }