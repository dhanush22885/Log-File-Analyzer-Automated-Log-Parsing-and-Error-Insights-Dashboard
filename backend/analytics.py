import re
from typing import Dict, Any, List
import pandas as pd


def normalize_error_message(message: str) -> str:
    """
    Strips variable tokens (IDs, numbers, IPs, durations) to normalize
    error patterns and group identical root causes together.
    """
    # Replace numbers, hex addresses, and IDs with <VAL>
    msg = re.sub(r"\b\d+\b", "<VAL>", message)
    # Replace IP addresses
    msg = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<IP>", msg)
    # Replace quoted strings/variables
    msg = re.sub(r"'[^']*'", "'<STR>'", msg)
    return msg.strip()


def compute_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes top-level statistical KPIs:
    Total volume, error count, warning count, error frequency percentage.
    """
    total_volume = int(len(df))
    if total_volume == 0:
        return {
            "total_volume": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "error_rate_pct": 0.0,
            "time_range": {"start": None, "end": None}
        }

    level_counts = df["level"].value_counts().to_dict()
    error_count = int(level_counts.get("ERROR", 0) + level_counts.get("CRITICAL", 0))
    warning_count = int(level_counts.get("WARNING", 0))
    info_count = int(level_counts.get("INFO", 0))
    
    error_rate_pct = round((error_count / total_volume) * 100, 2)

    # Safe datetime min/max handling
    clean_ts = df["timestamp"].dropna()
    start_ts = clean_ts.min().strftime("%Y-%m-%d %H:%M:%S") if not clean_ts.empty else None
    end_ts = clean_ts.max().strftime("%Y-%m-%d %H:%M:%S") if not clean_ts.empty else None

    return {
        "total_volume": total_volume,
        "error_count": error_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "error_rate_pct": error_rate_pct,
        "time_range": {"start": start_ts, "end": end_ts}
    }


def compute_distribution_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes breakdown distributions by log level and service source.
    """
    if df.empty:
        return {"level_distribution": {}, "source_distribution": {}, "source_error_distribution": {}}

    level_distribution = df["level"].value_counts().to_dict()
    source_distribution = df["source"].value_counts().to_dict()

    # Errors isolated by service source
    error_df = df[df["level"].isin(["ERROR", "CRITICAL"])]
    source_error_distribution = error_df["source"].value_counts().to_dict() if not error_df.empty else {}

    return {
        "level_distribution": level_distribution,
        "source_distribution": source_distribution,
        "source_error_distribution": source_error_distribution
    }


def compute_error_clusters(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Groups errors by their classified error_type and normalized message
    to reveal the most frequent root causes.
    """
    error_df = df[df["level"].isin(["ERROR", "CRITICAL"])].copy()
    if error_df.empty:
        return []

    # Create pattern column by stripping dynamic variables
    error_df["pattern"] = error_df["message"].apply(normalize_error_message)

    grouped = (
        error_df.groupby(["error_type", "pattern", "source"])
        .size()
        .reset_index(name="occurrence_count")
        .sort_values(by="occurrence_count", ascending=False)
        .head(top_n)
    )

    return grouped.to_dict(orient="records")


def compute_time_series(df: pd.DataFrame, freq: str = "1h") -> List[Dict[str, Any]]:
    """
    Aggregates log events and errors over time intervals for timeline graphing.
    """
    if df.empty or df["timestamp"].isna().all():
        return []

    valid_df = df.dropna(subset=["timestamp"]).copy()
    valid_df.set_index("timestamp", inplace=True)

    # Resample counts for all logs and errors specifically
    total_series = valid_df.resample(freq).size()
    error_series = valid_df[valid_df["level"].isin(["ERROR", "CRITICAL"])].resample(freq).size()

    timeline_df = pd.DataFrame({
        "timestamp": total_series.index.strftime("%Y-%m-%d %H:%M:%S"),
        "total_events": total_series.values,
        "error_events": error_series.reindex(total_series.index, fill_value=0).values
    })

    return timeline_df.to_dict(orient="records")