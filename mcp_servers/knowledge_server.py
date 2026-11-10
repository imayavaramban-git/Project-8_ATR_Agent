"""
MCP Server exposing knowledge base search capabilities.
"""
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP
from mcp_servers.mock_db import KNOWLEDGE_BASE

mcp = FastMCP("KnowledgeService")


@mcp.tool()
def search_help_docs(query: str) -> Dict[str, Any]:
    """Search knowledge base articles matching keywords in the query."""
    keywords = query.lower().split()
    matched_docs: List[Dict[str, str]] = []

    for doc in KNOWLEDGE_BASE:
        text = (doc["title"] + " " + doc["content"]).lower()
        if any(keyword in text for keyword in keywords):
            matched_docs.append(doc)

    return {
        "query": query,
        "matches_count": len(matched_docs),
        "results": matched_docs,
    }


if __name__ == "__main__":
    mcp.run()