<<<<<<< HEAD
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
=======
# 🔍 Automated Log Parsing & Error Insights Dashboard



An end-to-end operational observability platform that structures unstructured application logs, computes high-throughput diagnostic metrics, performs error pattern classification, and delivers an interactive diagnostic dashboard.

---

## 📌 Problem & Motivation

Distributed microservices generate massive volumes of unstructured plain-text logs. Analyzing failures in these environments introduces significant friction:
* **Manual Log Grepping:** Running ad-hoc shell commands (`grep`, `awk`, `tail`) through multi-gigabyte files during system incidents is error-prone and slow.
* **Variable Noise & Alert Fatigue:** Identical root causes are obscured because dynamic parameters (timestamps, host IDs, user IDs, IP addresses) prevent standard grouping.
* **Heavy Tooling Overhead:** Enterprise monitoring platforms (Datadog, Splunk, ELK stack) often introduce steep resource consumption, cloud licensing costs, and complex setup requirements for local development and lightweight staging environments.

**Solution:** A lightweight, dependency-minimal log intelligence tool built with **Python, Regex, Pandas, FastAPI, and Streamlit** that runs locally with zero infrastructure fees.

---


![ Dashboard1](images/image1)


![ Dashboard2](images/image2)


![ Dashboard3](images/image3)

## 🏗️ System Architecture

The application is decoupled into an analytical backend API and a reactive client dashboard:

```text
               ┌────────────────────────┐
               │    Raw .log / .txt     │
               └───────────┬────────────┘
                           │ (Upload)
                           ▼
               ┌────────────────────────┐
               │   FastAPI REST API     │
               │   (backend/main.py)    │
               └───────────┬────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌───────────────────┐       ┌────────────────────┐
   │   Regex Parser    │       │  Pandas Analytics  │
   │(backend/parser.py)│       │(backend/analytics) │
   └─────────┬─────────┘       └─────────┬──────────┘
             │                           │
             └─────────────┬─────────────┘
                           │ (JSON Responses)
                           ▼
               ┌────────────────────────┐
               │   Streamlit Frontend   │
               │   (frontend/app.py)    │
               │  - Plotly Visuals      │
               │  - Filter Explorer     │
               │  - Root Cause Matrix   │
               └────────────────────────┘


🚀 Key FeaturesRegex Extraction Engine: Uses named capture groups ((?P<timestamp>...), (?P<level>...), (?P<source>...), (?P<message>...)) to parse unstructured log streams into strongly typed tabular structures without brittle delimiter splitting.Statistical Performance Metrics: Vectorized calculations in Pandas derive system throughput, error and warning frequencies, and aggregate error-rate percentages.Root-Cause Pattern Normalization: Strips dynamic tokens (integers, IP addresses, quoted strings) using regex normalization to aggregate thousands of distinct trace lines into consolidated failure clusters.Time-Series Incident Trends: Resamples operational volume into hourly buckets (resample('1h')) to track failure spikes and request volume over time.RESTful Decoupled API: FastAPI backend serving validated JSON endpoints with interactive Swagger UI documentation.Interactive UI & Search: Plotly charts (service error heatmaps, severity donut breakdowns, timelines) paired with live multi-parameter filtering (level, source, free-text substring search).🛠️ Tech StackLanguage: Python 3.10+Data Processing & Analytics: Pandas, Regular Expressions (re)Backend API: FastAPI, Uvicorn, Pydantic, Python-MultipartFrontend Dashboard: Streamlit, Plotly ExpressTesting: PyTestHTTP Client: Requests


📁 Repository StructurePlaintextlog-analyzer/
├── backend/
│   ├── __init__.py
│   ├── parser.py          # Regex log parsing engine & error extraction
│   ├── analytics.py       # Pandas metrics, root-cause clustering, timelines
│   └── main.py            # FastAPI application endpoints
├── frontend/
│   └── app.py             # Streamlit dashboard & Plotly visual charts
├── sample_logs/
│   ├── generate_logs.py   # Synthetic multi-service log data generator
│   └── app.log            # Sample operational log dataset
├── tests/
│   ├── __init__.py
│   └── test_parser.py     # Unit tests for parser and analytics logic
├── requirements.txt       # Project dependencies
└── README.md



⚡ Quick Start Guide1. Clone the Repository & Set Up Virtual EnvironmentBashgit clone [https://github.com/](https://github.com/)<your-username>/log-file-analyzer.git
cd log-file-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
2. Generate Sample Log DataGenerate a realistic multi-service synthetic dataset (2,500 records with standard error distributions):Bashpython sample_logs/generate_logs.py
3. Run Automated TestsVerify parsing, pattern normalization, and metric computation:Bashpytest tests/
4. Start the ApplicationOpen two terminal sessions with the virtual environment activated:Terminal 1 — FastAPI Backend:Bashuvicorn backend.main:app --reload --port 8000
API Swagger Documentation is available at: http://127.0.0.1:8000/docsTerminal 2 — Streamlit Frontend:Bashstreamlit run frontend/app.py
Dashboard will launch at: http://localhost:8501📊 API Documentation & EndpointsMethodEndpointDescriptionGET/healthVerifies API health and loaded dataset row count.POST/api/uploadIngests .log or .txt files and parses entries into memory.GET/api/analytics/summaryReturns total volume, error count, warning count, and error rate %.GET/api/analytics/distributionsReturns breakdowns by log level and service origin.GET/api/analytics/error-clustersReturns top grouped root causes with normalized error patterns.GET/api/analytics/timelineReturns resampled time-series event and error arrays.GET/api/logsPaginated search endpoint supporting level, source, and search query parameters.📈 Dashboard Preview & CapabilitiesAnalytics Overview: Visualizes error density across microservices (payment_gateway, auth_service, db_pool, etc.) and displays event volume timelines to spot failure cascades.Root Cause Clusters: Consolidates repetitive errors by masking variables into <VAL>, <IP>, and '<STR>', identifying top offenders at a glance.Log Search & Explorer: Enables engineers to quickly pinpoint target records using severity filters, source selection, and instant keyword searches.
>>>>>>> 2431159534be7a3a26884791a6b6293f6bd49295
