"""
LangGraph state machine wiring the ticket resolution flow.
"""
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.understand import understand_ticket_node
from agent.nodes.plan import plan_resolution_node
from agent.nodes.tool_caller import check_facts_node
from agent.nodes.guardrail import guardrail_check_node
from agent.nodes.resolve import resolve_ticket_node
from agent.nodes.escalate import escalate_ticket_node


def route_after_guardrail(state: AgentState) -> str:
    """Conditional router based on guardrail check outcome."""
    if state.get("policy_passed"):
        return "resolve"
    return "escalate"


def build_ticket_agent_graph():
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("understand", understand_ticket_node)
    workflow.add_node("plan", plan_resolution_node)
    workflow.add_node("check_facts", check_facts_node)
    workflow.add_node("guardrail", guardrail_check_node)
    workflow.add_node("resolve", resolve_ticket_node)
    workflow.add_node("escalate", escalate_ticket_node)

    # Define edges
    workflow.set_entry_point("understand")
    workflow.add_edge("understand", "plan")
    workflow.add_edge("plan", "check_facts")
    workflow.add_edge("check_facts", "guardrail")

    # Conditional branching
    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "resolve": "resolve",
            "escalate": "escalate",
        },
    )

    workflow.add_edge("resolve", END)
    workflow.add_edge("escalate", END)

    return workflow.compile()


# Compiled singleton instance
ticket_agent_app = build_ticket_agent_graph()