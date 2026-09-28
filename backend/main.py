from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from backend.parser import parse_logs_to_dataframe
from backend.analytics import (
    compute_summary_metrics,
    compute_distribution_metrics,
    compute_error_clusters,
    compute_time_series,
)

app = FastAPI(
    title="Log File Analyzer API",
    description="Automated log parsing, statistical aggregation, and error pattern classification.",
    version="1.0.0"
)

# Enable CORS for local cross-origin communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active session dataset
GLOBAL_LOG_STORE: Dict[str, Any] = {
    "df": pd.DataFrame(),
    "filename": None
}


class HealthResponse(BaseModel):
    status: str
    active_dataset_rows: int
    loaded_file: Optional[str]


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health probe indicating current loaded log file status."""
    df = GLOBAL_LOG_STORE["df"]
    return {
        "status": "healthy",
        "active_dataset_rows": len(df),
        "loaded_file": GLOBAL_LOG_STORE["filename"]
    }


@app.post("/api/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """
    Accepts a log file (.log, .txt), parses entries via regex,
    and indexes them in memory for analysis.
    """
    if not (file.filename.endswith(".log") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .log and .txt files are supported.")

    content_bytes = await file.read()
    raw_content = content_bytes.decode("utf-8", errors="replace")

    df = parse_logs_to_dataframe(raw_content)
    if df.empty:
        raise HTTPException(status_code=422, detail="No valid log lines could be extracted.")

    GLOBAL_LOG_STORE["df"] = df
    GLOBAL_LOG_STORE["filename"] = file.filename

    return {
        "message": f"Successfully parsed and loaded '{file.filename}'",
        "records_count": len(df),
        "columns": list(df.columns)
    }


@app.get("/api/analytics/summary")
def get_summary_metrics():
    """Returns top-level KPIs: volume, error/warning frequencies, error rate."""
    df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        raise HTTPException(status_code=404, detail="No log data loaded. Upload a file first.")
    return compute_summary_metrics(df)


@app.get("/api/analytics/distributions")
def get_distributions():
    """Returns categorical breakdowns across log levels and services."""
    df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        raise HTTPException(status_code=404, detail="No log data loaded. Upload a file first.")
    return compute_distribution_metrics(df)


@app.get("/api/analytics/error-clusters")
def get_error_clusters(top_n: int = Query(5, ge=1, le=50)):
    """Groups similar errors together to reveal top root causes."""
    df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        raise HTTPException(status_code=404, detail="No log data loaded. Upload a file first.")
    return compute_error_clusters(df, top_n=top_n)


@app.get("/api/analytics/timeline")
def get_timeline(interval: str = Query("1h", regex="^(1h|30min|15min|1D)$")):
    """Aggregates log events and errors over time intervals for charting."""
    df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        raise HTTPException(status_code=404, detail="No log data loaded. Upload a file first.")
    return compute_time_series(df, freq=interval)


@app.get("/api/logs")
def search_and_filter_logs(
    level: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Search and filter endpoint for raw parsed logs.
    Supports filtering by level, source, and free-text substring search.
    """
    df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        return {"total": 0, "logs": []}

    filtered_df = df.copy()

    if level and level.upper() != "ALL":
        filtered_df = filtered_df[filtered_df["level"] == level.upper()]

    if source and source.lower() != "all":
        filtered_df = filtered_df[filtered_df["source"] == source]

    if search:
        search_pattern = re.escape(search)
        filtered_df = filtered_df[
            filtered_df["message"].str.contains(search_pattern, case=False, na=False)
        ]

    total_matches = len(filtered_df)
    
    # Paginate and format timestamps for JSON serialization
    paged_df = filtered_df.iloc[offset: offset + limit].copy()
    paged_df["timestamp"] = paged_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "total": total_matches,
        "offset": offset,
        "limit": limit,
        "logs": paged_df.to_dict(orient="records")
    }
    def get_filtered_df(level: Optional[str] = None, source: Optional[str] = None) -> pd.DataFrame:
        df = GLOBAL_LOG_STORE["df"]
    if df.empty:
        return df
    filtered = df.copy()
    if level and level.upper() != "ALL":
        filtered = filtered[filtered["level"] == level.upper()]
    if source and source.lower() != "all":
        filtered = filtered[filtered["source"] == source]
    return filtered

    @app.get("/api/analytics/summary")
    def get_summary_metrics(level: Optional[str] = None, source: Optional[str] = None):
        df = get_filtered_df(level, source)
        if df.empty:
            raise HTTPException(status_code=404, detail="No log data matches the filter.")
        return compute_summary_metrics(df)