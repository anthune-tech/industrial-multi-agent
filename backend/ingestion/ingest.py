import pandas as pd
from pathlib import Path


def ingest_csv(filepath: str | Path, table: str = "production_log") -> int:
    """Ingest a CSV file into the raw data store (SQLite)."""
    db_path = Path(__file__).parent.parent / "data" / "raw.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(filepath)
    df.to_sql(table, f"sqlite:///{db_path}", if_exists="append", index=False)
    return len(df)


def seed_sample_data():
    """Generate and ingest sample plant data."""
    import random
    from datetime import datetime, timedelta

    machines = [f"LINE-{i:02d}" for i in range(1, 6)]
    shifts = ["morning", "afternoon", "night"]
    rows = []

    base = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    for day_offset in range(7):
        for machine in machines:
            for shift in shifts:
                ts = base - timedelta(days=day_offset)
                total = random.randint(80, 120)
                good = random.randint(total - 20, total)
                bad = total - good
                downtime = random.choice([0, 0, 0, 5, 10, 15, 30])
                rows.append({
                    "timestamp": ts.isoformat(),
                    "machine_id": machine,
                    "shift": shift,
                    "total_parts": total,
                    "good_parts": good,
                    "bad_parts": bad,
                    "downtime_minutes": downtime,
                    "cycle_time_sec": round(random.uniform(38, 52), 1),
                    "run_status": "down" if downtime > 15 else ("idle" if downtime > 5 else "running"),
                })

    df = pd.DataFrame(rows)
    db_path = Path(__file__).parent.parent / "data" / "raw.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_sql("production_log", f"sqlite:///{db_path}", if_exists="replace", index=False)
    print(f"Seeded {len(df)} rows into {db_path}")
    return len(df)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed_sample_data()
    else:
        print("Usage: python -m ingestion.ingest seed")
