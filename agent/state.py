from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Core ticket information
    ticket_id: str
    customer_id: str
    subject: str
    message: str
    
    # Internal agent tracking
    intent: Optional[str]
    extracted_entities: Dict[str, Any]
    current_plan: List[Dict[str, Any]]
    
    # Execution logs & tool observations
    gathered_facts: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    
    # Guardrail and safety checks
    confidence_score: float
    policy_passed: bool
    policy_failures: List[str]
    
    # Final outputs
    final_status: Optional[str]
    final_reply: Optional[str]
    escalation_diagnosis: Optional[Dict[str, Any]]