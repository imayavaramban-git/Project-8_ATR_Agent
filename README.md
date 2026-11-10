# ResolveAI: Autonomous Ticket Resolution Agent (ATR)

An enterprise-ready Autonomous Ticket Resolution system engineered using **LangGraph**, **FastAPI**, and the **Model Context Protocol (MCP)**. ResolveAI inspects customer support queries, fetches business state via isolated MCP servers, enforces policy safety guardrails, and either executes resolutions automatically or routes edge cases to human operators with complete diagnostic context.

## 1. System Architecture & Workflow

```
[Inbound Customer Ticket]
           │
           ▼
[FastAPI Gateway: POST /tickets/resolve]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│               LangGraph State Machine                  │
│                                                        │
│  [Understand Node]                                     │
│  ├── Intent Classification (Heuristic / LLM)           │
│  └── Entity Extraction (order_id, email, amount)       │
│           │                                            │
│           ▼                                            │
│  [Plan Node]                                           │
│  └── Selects MCP tool actions & parameters             │
│           │                                            │
│           ▼                                            │
│  [Tool Caller Node] ─── queries ───> [MCP Servers]    │
│  └── Gathers facts (status, account, docs)             │
│           │                                            │
│           ▼                                            │
│  [Guardrail Node]                                      │
│  ├── Check: Confidence >= 0.80                         │
│  ├── Check: Max automated refund <= $100               │
│  └── Check: Account locked / delivery validation       │
└───────────┬────────────────────────────────────────────┘
            │
      ┌─────┴─────────────────────────┐
      │ Passed                        │ Failed Policy
      ▼                               ▼
[Resolve Node]                 [Escalate Node]
├── Trigger MCP tool actions   ├── Construct diagnosis
└── Synthesize customer reply  └── Flag recommended human actions
      │                               │
      └──────────────┬────────────────┘
                     ▼
          [TicketResponse Payload]

```

## 2. Repository Layout

```
Project 8_ATR_Agent/
├── agent/
│   ├── nodes/
│   │   ├── escalate.py         # Human escalation & diagnostic packaging
│   │   ├── guardrail.py        # Policy enforcement & threshold checks
│   │   ├── plan.py             # Action & tool planner
│   │   ├── resolve.py          # Response generation & action resolution
│   │   ├── tool_caller.py      # MCP tool client dispatch
│   │   └── understand.py       # Intent & entity extraction
│   ├── graph.py                # LangGraph StateGraph assembly
│   ├── prompts.py              # System prompts & guidelines
│   └── state.py                # AgentState TypedDict definition
├── api/
│   └── main.py                 # FastAPI application, /healthz & /tickets/resolve
├── evals/
│   ├── eval_dataset.json       # Production test cases & expected outcomes
│   └── run_evals.py            # AI agent evaluation benchmark runner
├── mcp_servers/
│   ├── kb_search_server.py     # MCP tool for knowledge base lookups
│   └── order_account_server.py # MCP tools for orders, refunds, and resets
├── models/
│   └── ticket.py               # Pydantic schemas (TicketPayload, TicketResponse)
├── tests/
│   ├── test_agent_graph.py     # Graph end-to-end integration tests
│   ├── test_api.py             # FastAPI endpoint tests
│   ├── test_evals.py           # Evaluation gate pytest runner
│   ├── test_mcp_servers.py     # MCP tool unit tests
│   └── test_schemas.py         # Pydantic schema validation tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # Automated GitHub Actions test & build pipeline
├── docker-compose.yml          # Container multi-service orchestration
├── Dockerfile.api              # Container image for FastAPI agent
├── Dockerfile.mcp              # Container image for MCP tool service
└── requirements.txt            # Python dependencies (pinned mcp<2.0.0)

```

## 3. Policy Rules & Guardrails

| Policy ID | Rule Target | Validation Rule | Action on Failure | 
| ----- | ----- | ----- | ----- | 
| `POL-01` | Intent Confidence | Intent classification score must be $\ge 0.80$ | Escalate to general support with low-confidence diagnosis. | 
| `POL-02` | Automated Refunds | Total refund amount must be $\le \$100.00$ | Escalate to tier-2 human supervisor for payment review. | 
| `POL-03` | Delivery Check | Order status must be `'delivered'` to refund | Refuse automated refund; recommend tracking verification. | 
| `POL-04` | Account Security | Reset denied if account is locked (`'locked'`) | Escalate to security operations; require verification. | 

## 4. Local Installation & Development

### Virtual Environment Setup

```
# Create and activate environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

```

### Running Tests

Execute all 22 automated tests covering schemas, MCP server logic, routing, and endpoints:

```
python -m pytest tests/ -v

```

### Running the AI Evaluation Gate

Execute the 5-scenario benchmark suite:

```
python evals/run_evals.py

```

Expected result:

```
=================================================================
       RESOLVEAI AGENT EVALUATION BENCHMARK SUITE
=================================================================
  [PASS] EVAL-01: Order status inquiry for delivered item
  [PASS] EVAL-02: Valid refund request under threshold ($49.99 <= $100.00)
  [PASS] EVAL-03: Excessive refund amount policy violation ($250 > $100) -> Must escalate
  [PASS] EVAL-04: Valid password reset request with valid email
  [PASS] EVAL-05: Ambiguous/Unknown message -> Must escalate due to low confidence
-----------------------------------------------------------------
Total Evaluated: 5 | Passed: 5 | Pass Rate: 100.0%
=================================================================
[+] All evaluation gates passed. Safe to ship.

```

## 5. Docker Deployment

### Start Services

```
docker compose up -d --build
docker compose ps

```

### Health Probe

```
Invoke-RestMethod -Uri http://localhost:8000/healthz

```

## 6. End-to-End Resolution Demonstration

### Scenario: Order Status Inquiry for Delivered Item

#### Inbound Request Payload

```
$ticket = @{
    ticket_id = "TICK-LIVE-001"
    customer_id = "CUST-001"
    subject = "Status for ORD-1001"
    message = "Can you please check the tracking on my order ORD-1001?"
    metadata = @{ channel = "web" }
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/tickets/resolve -Method Post -Body $ticket -ContentType "application/json"

```

#### Lifecycle Trace

1. **Understand**: Extracted intent `order_status` and identifier `order_id = "ORD-1001"` (confidence: 0.95).

2. **Plan**: Scheduled `get_order_status` execution.

3. **Tool Caller**: Queried MCP server; returned status `delivered` with items `["Wireless Mouse", "USB-C Cable"]`.

4. **Guardrail**: Validated confidence $\ge 0.80$ and confirmed valid order record. Guardrail passed.

5. **Resolve**: Generated friendly customer notification and set resolution status to `resolved`.

#### Outbound Response Payload

```
{
  "ticket_id": "TICK-LIVE-001",
  "status": "resolved",
  "response_message": "Hello, your order ORD-1001 is currently 'delivered'. Items: Wireless Mouse, USB-C Cable.",
  "escalation_diagnosis": null,
  "actions_taken": []
}

```

## 7. Adding New Capabilities

New agent workflows can be integrated into the architecture via two minimal steps:

1. **Write the MCP Tool (`mcp_servers/`)**:
   Define the standalone Python tool function with the necessary parameter schemas and business logic.

2. **Add a Policy Entry (`agent/nodes/guardrail.py`)**:
   Add an entry into the policy dictionary specifying permission boundaries, financial caps, or required preconditions.