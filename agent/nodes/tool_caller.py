from agent.state import AgentState
from mcp_servers.order_account_server import get_order_status
from mcp_servers.knowledge_server import search_help_docs


def check_facts_node(state: AgentState) -> dict:
    """Execute read-only tools to gather facts before any write action."""
    facts = dict(state.get("gathered_facts", {}))
    plan = state.get("current_plan", [])

    for step in plan:
        tool_name = step.get("tool")
        args = step.get("args", {})

        if tool_name == "get_order_status" and args.get("order_id"):
            facts["order_status"] = get_order_status(args["order_id"])

        elif tool_name == "search_help_docs" and args.get("query"):
            facts["docs_search"] = search_help_docs(args["query"])

    return {"gathered_facts": facts}