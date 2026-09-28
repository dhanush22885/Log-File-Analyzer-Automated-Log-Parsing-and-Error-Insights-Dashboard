# Automated Log Parsing & Error Insights Dashboard

An end-to-end log parsing, statistical aggregation, and error diagnostic platform built with **Python, Regex, Pandas, FastAPI, and Streamlit**.

## Features

- **Regex Log Parsing Engine:** Parses timestamps, severity levels, microservice sources, and messages into structured tabular records.
- **Statistical Analytics:** Computes overall event throughput, error/warning frequencies, error-rate KPIs, and hourly timelines using Pandas.
- **Root-Cause Clustering:** Normalizes dynamic tokens (user IDs, IPs, durations) to isolate recurring failure patterns and top offending services.
- **FastAPI REST API:** Asynchronous API supporting multi-part file uploads, search filtering, and analytical endpoints.
- **Interactive UI (Streamlit & Plotly):** Live dashboards with multi-service error heatmaps, log-level distributions, and interactive record explorer.

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pandas, Pydantic
- **Frontend:** Streamlit, Plotly
- **Testing:** PyTest

## Getting Started

### 1. Setup Virtual Environment
```bash
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt