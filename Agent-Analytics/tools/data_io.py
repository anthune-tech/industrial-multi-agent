import json
from pathlib import Path

import pandas as pd
from langchain.tools import tool

RAW_DB_PATH = Path(__file__).parent.parent / "data" / "raw.db"


@tool("Read Plant Data")
def read_plant_data(machine_id: str, start_date: str, end_date: str) -> str:
    """Read raw plant production data for a machine within a date range.
    Returns JSON-formatted data. Falls back to mock data if no real data exists."""
    if RAW_DB_PATH.exists():
        try:
            df = pd.read_sql(
                "SELECT * FROM production_log WHERE machine_id = ? AND timestamp >= ? AND timestamp <= ?",
                f"sqlite:///{RAW_DB_PATH}",
                params=(machine_id, start_date, end_date),
            )
            if not df.empty:
                return df.rename(columns={
                    "good_parts": "good_count",
                    "bad_parts": "bad_count",
                    "total_parts": "total_count",
                }).to_json(orient="records", date_format="iso")
        except Exception:
            pass

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