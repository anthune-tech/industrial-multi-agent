import json
from langchain.tools import tool


@tool("Query Knowledge Base")
def query_knowledge_base(query: str, n_results: int = 5) -> str:
    """Search the plant knowledge base for relevant documentation,
    troubleshooting guides, machine profiles, and maintenance procedures.
    Returns a JSON list of matching documents with content and metadata."""
    from db.knowledge_base import query_knowledge

    results = query_knowledge(query, n_results=n_results)
    return json.dumps(results, indent=2)
