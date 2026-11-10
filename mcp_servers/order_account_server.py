"""
MCP Server exposing tools for Orders, Refunds, and Password Resets.
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp_servers.mock_db import ORDERS_DB, USERS_DB
import time

mcp = FastMCP("OrderAccountService")


@mcp.tool()
def get_order_status(order_id: str) -> Dict[str, Any]:
    """Retrieve details and status for a given order ID."""
    order = ORDERS_DB.get(order_id.strip())
    if not order:
        return {"found": False, "message": f"Order {order_id} not found."}
    return {"found": True, "order": order}


@mcp.tool()
def process_refund(order_id: str, amount: float, reason: str) -> Dict[str, Any]:
    """
    Process a refund for an order.
    Returns success status and updated refund details.
    """
    order = ORDERS_DB.get(order_id.strip())
    if not order:
        return {"success": False, "message": f"Order {order_id} does not exist."}

    if order["status"] != "delivered":
        return {
            "success": False,
            "message": f"Cannot refund order in status '{order['status']}'. Must be 'delivered'.",
        }

    if amount > order["total_amount"]:
        return {
            "success": False,
            "message": f"Requested refund amount ${amount} exceeds order total ${order['total_amount']}.",
        }

    order["refund_status"] = "processed"
    order["refund_amount"] = amount
    order["refund_reason"] = reason

    return {
        "success": True,
        "message": f"Refund of ${amount:.2f} processed for order {order_id}.",
        "order_id": order_id,
        "refund_amount": amount,
    }


@mcp.tool()
def trigger_password_reset(email: str) -> Dict[str, Any]:
    """
    Triggers a secure password reset email to the given address.
    """
    clean_email = email.strip().lower()
    user = USERS_DB.get(clean_email)
    if not user:
        return {"success": False, "message": f"No account found with email {clean_email}."}

    if user["status"] == "locked":
        return {
            "success": False,
            "message": "Account is locked. Automated reset disallowed; manual verification required.",
        }

    user["reset_token_sent"] = True
    return {
        "success": True,
        "message": f"Password reset instructions sent to {clean_email}.",
    }


if __name__ == "__main__":
    import sys
    print("OrderAccountService MCP server started.", flush=True)
    try:
        # If running interactively via stdio
        if not sys.stdin.isatty():
            mcp.run()
        else:
            while True:
                time.sleep(3600)
    except Exception as e:
        print(f"Server loop error: {e}", flush=True)
        while True:
            time.sleep(3600)