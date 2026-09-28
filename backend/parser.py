import re
from typing import List, Dict, Any, Optional
import pandas as pd

# Matches: 2026-09-28 12:45:10 [LEVEL] [source_name] Actual message text
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<level>[A-Z]+)\]\s+"
    r"\[(?P<source>[\w\.\-]+)\]\s+"
    r"(?P<message>.*)$"
)

# Common exception regex to isolate error classes from error messages
ERROR_CLASS_PATTERN = re.compile(r"^([A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception|[A-Za-z0-9_]+Timeout|[A-Za-z0-9_]+Failed)")

def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parses a single log string into structured fields using named regex groups.
    """
    cleaned_line = line.strip()
    if not cleaned_line:
        return None

    match = LOG_PATTERN.match(cleaned_line)
    if not match:
        # Handles unstructured or malformed log lines gracefully
        return {
            "timestamp": None,
            "level": "UNKNOWN",
            "source": "unparsed",
            "message": cleaned_line,
            "error_type": "Unclassified"
        }

    data = match.groupdict()
    level = data["level"].upper()
    message = data["message"]
    
    # Extract error class for grouping if level indicates failure
    error_type = "None"
    if level in ["ERROR", "CRITICAL"]:
        err_match = ERROR_CLASS_PATTERN.search(message)
        error_type = err_match.group(1) if err_match else "GeneralError"
    elif level == "WARNING":
        error_type = "WarningEvent"

    data["error_type"] = error_type
    return data

def parse_logs_to_dataframe(log_content: str) -> pd.DataFrame:
    """
    Parses a multi-line log string or file content into a strongly typed Pandas DataFrame.
    """
    records: List[Dict[str, Any]] = []
    
    for line in log_content.splitlines():
        parsed = parse_log_line(line)
        if parsed:
            records.append(parsed)

    if not records:
        return pd.DataFrame(columns=["timestamp", "level", "source", "message", "error_type"])

    df = pd.DataFrame(records)
    
    # Convert timestamp column to datetime; invalid parses coerced to NaT
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    return df