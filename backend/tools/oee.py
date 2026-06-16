import json
from datetime import datetime
from langchain.tools import tool


@tool("Calculate OEE")
def calculate_oee(machine_id: str, shift: str, date: str) -> str:
    """Calculate Overall Equipment Effectiveness for a machine on a given shift.
    Returns availability, performance, quality, and overall OEE."""
    from tools.data_io import read_plant_data

    if date == "today":
        date = datetime.now().strftime("%Y-%m-%d")

    raw = json.loads(read_plant_data.invoke({
        "machine_id": machine_id,
        "start_date": date,
        "end_date": date,
    }))
    if not raw:
        return json.dumps({"error": "No data available"})

    total_time = len(raw) * 60
    down_time = sum(60 for r in raw if r["run_status"] == "down")
    idle_time = sum(60 for r in raw if r["run_status"] == "idle")
    run_time = total_time - down_time - idle_time

    availability = run_time / total_time if total_time > 0 else 0

    ideal_cycle_min = 40 / 60
    total_parts = sum(r["total_count"] for r in raw)
    performance = (ideal_cycle_min * total_parts) / run_time if run_time > 0 else 0
    performance = min(performance, 1.0)

    good = sum(r["good_count"] for r in raw)
    quality = good / total_parts if total_parts > 0 else 0

    oee = availability * performance * quality

    return json.dumps({
        "machine_id": machine_id,
        "shift": shift,
        "date": date,
        "availability": round(availability, 3),
        "performance": round(performance, 3),
        "quality": round(quality, 3),
        "oee": round(oee, 3),
        "run_time_min": run_time,
        "down_time_min": down_time,
        "idle_time_min": idle_time,
    })