from pathlib import Path
from typing import Any
import pandas as pd

EXPECTED_COLUMNS = [
    "engine_id",
    "cycle",
    "operational_setting_1",
    "operational_setting_2",
    "operational_setting_3",
    "sensor_1",
    "sensor_2",
    "sensor_3",
]

def process_telemetry(file_path: Path) -> dict[str,Any]:
    #reads csv file and returns summary of statistics
    df = pd.read_csv(file_path)
    
    if df.empty:
        raise ValueError("CSV contains no data")
    
    missing = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    sensor_columns = [
        column
        for column in df.columns
        if column.startswith("sensor_")
    ]

    summary = {
        "rows": int(len(df)),
        "engines": int(df["engine_id"].nunique()),
        "min_cycle": int(df["cycle"].min()),
        "max_cycle":int(df["cycle"].max()),
        "sensor_statistics": {}
    }

    for sensor in sensor_columns:
        summary["sensor_statistics"][sensor] = {
            "mean": float(df[sensor].mean()),
            "min": float(df[sensor].min()),
            "max": float(df[sensor].max()),
        }

    return summary