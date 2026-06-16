import json
from langchain.tools import tool


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