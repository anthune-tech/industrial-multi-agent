import pandas as pd
from crewai.tools import tool


@tool("Read Plant Data")
def read_plant_data(machine_id: str, start_date: str, end_date: str) -> str:
    """Read raw plant production data for a machine within a date range.
    Returns JSON-formatted data."""
    data = pd.DataFrame({
        "timestamp": pd.date_range(start=start_date, periods=10, freq="h"),
        "machine_id": machine_id,
        "run_status": ["running", "running", "running", "down", "running",
                       "running", "idle", "running", "running", "running"],
        "cycle_time_sec": [45, 42, 44, 0, 46, 43, 0, 41, 44, 45],
        "good_count": [95, 98, 97, 0, 94, 96, 0, 99, 97, 95],
        "bad_count": [5, 2, 3, 0, 6, 4, 0, 1, 3, 5],
        "total_count": [100, 100, 100, 0, 100, 100, 0, 100, 100, 100],
    })
    return data.to_json(orient="records", date_format="iso")
