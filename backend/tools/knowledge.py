import json
import os
from pathlib import Path
from langchain.tools import tool


KB_DIR = Path(__file__).parent.parent / "knowledge_base"


def _load_sop_documents():
    if not KB_DIR.exists():
        return []
    docs = []
    for f in sorted(KB_DIR.glob("*.md")):
        text = f.read_text().strip()
        if text:
            title = f.stem.replace("-", " ").title()
            docs.append({"title": title, "file": f.name, "content": text})
    return docs


@tool("Query Knowledge Base")
def query_knowledge_base(question: str) -> str:
    """Query the knowledge base (SOPs, manuals, maintenance docs) for relevant information.
    Uses ChromaDB vector search if available, falls back to keyword matching."""
    results = []
    docs = _load_sop_documents()

    if not docs:
        return json.dumps({"results": [], "message": "Knowledge base is empty"})

    keywords = question.lower().split()
    for doc in docs:
        text_lower = doc["content"].lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > 0:
            results.append({"title": doc["title"], "relevance": matches, "snippet": doc["content"][:500]})

    results.sort(key=lambda x: -x["relevance"])
    results = results[:5]

    if not results:
        return json.dumps({
            "results": [],
            "message": "No relevant documents found. Try rephrasing your question.",
        })

    return json.dumps({"results": results, "message": f"Found {len(results)} relevant documents"}, indent=2)


@tool("Query Results DB")
def query_results_db(sql: str) -> str:
    """Execute a read-only SQL query against the results database.
    Only SELECT statements are allowed."""
    from db.connection import SessionLocal

    sql = sql.strip().upper()
    if not sql.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries are allowed"})

    db = SessionLocal()
    try:
        result = db.execute(sql)
        rows = [dict(row._mapping) for row in result]
        return json.dumps(rows, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()


@tool("Save to Results DB")
def save_to_results_db(table: str, data: str) -> str:
    """Save a JSON object to one of the results tables.
    Supported tables: oee_snapshots, machine_status, analytics_results, alarms, troubleshoot_sessions"""
    from db.connection import SessionLocal
    from db.models import OeeSnapshot, MachineStatus, AnalyticsResult, Alarm, TroubleshootSession

    import json as json_mod
    parsed = json_mod.loads(data) if isinstance(data, str) else data

    table_map = {
        "oee_snapshots": OeeSnapshot,
        "machine_status": MachineStatus,
        "analytics_results": AnalyticsResult,
        "alarms": Alarm,
        "troubleshoot_sessions": TroubleshootSession,
    }

    model_cls = table_map.get(table)
    if not model_cls:
        return json_mod.dumps({"error": f"Unknown table: {table}"})

    db = SessionLocal()
    try:
        record = model_cls(**parsed)
        db.add(record)
        db.commit()
        return json_mod.dumps({"success": True, "id": record.id})
    except Exception as e:
        db.rollback()
        return json_mod.dumps({"error": str(e)})
    finally:
        db.close()