import json
from langchain.tools import tool


@tool("Detect Anomalies")
def detect_anomalies(machine_id: str, metric: str) -> str:
    """Detect statistical anomalies in a machine's metric data."""
    from tools.analytics import analyze_trend

    return analyze_trend(machine_id, metric, period_days=1)


@tool("Generate Report")
def generate_report(machine_id: str, period_days: int = 1) -> str:
    """Generate a structured summary report for a machine over a period."""
    from tools.oee import calculate_oee
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")
    oee_data = json.loads(calculate_oee(machine_id, "all", today))

    report = {
        "machine_id": machine_id,
        "period_days": period_days,
        "report_date": today,
        "oee_summary": oee_data,
        "status": "Report generated successfully",
    }
    return json.dumps(report, indent=2)


@tool("Save Troubleshoot Session")
def save_troubleshoot_session(machine_id: str, problem: str,
                              diagnosis: str, resolution: str,
                              confidence: float = 0.0) -> str:
    """Save a troubleshooting session to the database."""
    from tools.knowledge import save_to_results_db

    data = json.dumps({
        "machine_id": machine_id,
        "problem": problem,
        "diagnosis": diagnosis,
        "resolution": resolution,
        "confidence": confidence,
    })
    return save_to_results_db("troubleshoot_sessions", data)
