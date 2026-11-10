"""
FastAPI entrypoint for ResolveAI Ticket Resolution Agent.
"""
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status

from models.ticket import (
    TicketPayload,
    TicketResponse,
    TicketResolutionStatus,
    HumanEscalationDiagnosis,
)
from agent.graph import ticket_agent_app

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("resolve_ai_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ResolveAI API service starting up...")
    yield
    logger.info("ResolveAI API service shutting down...")


app = FastAPI(
    title="ResolveAI - Autonomous Ticket Resolution Agent",
    description="Production-grade API for autonomous ticket triage, resolution, and escalation.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check() -> Dict[str, str]:
    """Health check endpoint used by Docker and cloud load balancers."""
    return {"status": "healthy", "service": "resolve-ai"}


@app.post(
    "/tickets/resolve",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tickets"],
)
def resolve_ticket(ticket: TicketPayload) -> TicketResponse:
    """
    Ingest an incoming ticket, trigger LangGraph autonomous reasoning,
    and return the resolution or escalation diagnosis.
    """
    logger.info(f"Received ticket {ticket.ticket_id} from customer {ticket.customer_id}")

    try:
        # Initialize graph state
        initial_state = {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "subject": ticket.subject,
            "message": ticket.message,
            "gathered_facts": {},
            "actions_taken": [],
            "policy_failures": [],
        }

        # Run state machine
        final_state = ticket_agent_app.invoke(initial_state)

        # Parse escalation diagnosis if escalated
        escalation_diag = None
        if final_state.get("escalation_diagnosis"):
            escalation_diag = HumanEscalationDiagnosis(**final_state["escalation_diagnosis"])

        response = TicketResponse(
            ticket_id=ticket.ticket_id,
            status=TicketResolutionStatus(final_state["final_status"]),
            response_message=final_state.get("final_reply", "Ticket processed."),
            escalation_diagnosis=escalation_diag,
            actions_taken=final_state.get("actions_taken", []),
        )

        logger.info(
            f"Ticket {ticket.ticket_id} processed with outcome: {response.status.value}"
        )
        return response

    except Exception as e:
        logger.error(f"Error processing ticket {ticket.ticket_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal agent error processing ticket: {str(e)}",
        )