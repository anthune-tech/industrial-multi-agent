import json

import numpy as np
from crewai.tools import tool


@tool("Analyze Trend")
def analyze_trend(machine_id: str, metric: str, period_days: int = 7) -> str:
    """Analyze trend for a given metric over a period. Returns stats and anomalies."""
    from tools.data_io import read_plant_data

    import pandas as pd

    end = pd.Timestamp.now().strftime("%Y-%m-%d")
    start = (pd.Timestamp.now() - pd.Timedelta(days=period_days)).strftime("%Y-%m-%d")
    raw = json.loads(read_plant_data(machine_id, start, end))
    if not raw:
        return json.dumps({"error": "No data available"})

    df = pd.DataFrame(raw)
    metric_map = {"cycle_time": "cycle_time_sec", "good_count": "good_count",
                  "bad_count": "bad_count", "total_count": "total_count"}
    col = metric_map.get(metric, metric)
    if col not in df.columns:
        return json.dumps({"error": f"Metric {metric} not found"})

    values = df[col].replace(0, np.nan).dropna().values
    if len(values) == 0:
        return json.dumps({"error": "No valid data points"})

    mean = float(np.mean(values))
    std = float(np.std(values))
    z_scores = np.abs((values - mean) / (std + 1e-8))
    anomalies = [{"index": int(i), "value": float(v)}
                 for i, v in enumerate(values) if z_scores[i] > 2.5]

    return json.dumps({
        "machine_id": machine_id,
        "metric": metric,
        "period_days": period_days,
        "mean": round(mean, 2),
        "std": round(std, 2),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "num_anomalies": len(anomalies),
        "anomalies": anomalies[:10],
    })
