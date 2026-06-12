import pandas as pd
from pathlib import Path


def ingest_csv(filepath: str | Path, table: str = "oee_snapshots"):
    """Ingest a CSV file into the raw data store (SQLite)."""
    df = pd.read_csv(filepath)
    df.to_sql(table, "sqlite:///data/raw.db", if_exists="append", index=False)
    return len(df)
