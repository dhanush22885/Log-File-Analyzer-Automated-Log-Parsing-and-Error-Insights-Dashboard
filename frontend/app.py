import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Log File Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        padding: 1.2rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 5px solid #0066cc;
    }
    .badge-error { color: #d9534f; font-weight: bold; }
    .badge-warning { color: #f0ad4e; font-weight: bold; }
    .badge-info { color: #5bc0de; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Automated Log Parsing & Error Insights Dashboard")
st.caption("Engineered with Python, Regex, Pandas, FastAPI & Streamlit")

# Check Backend Health
@st.cache_data(ttl=5)
def check_backend_status():
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if res.status_code == 200:
            return res.json()
    except requests.exceptions.RequestException:
        return None
    return None

backend_info = check_backend_status()

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.header("⚙️ Data Ingestion")
    
    if backend_info:
        st.success(f"Backend Connected")
        if backend_info.get("loaded_file"):
            st.info(f"Loaded: `{backend_info['loaded_file']}`\n({backend_info['active_dataset_rows']} rows)")
    else:
        st.error("Backend Disconnected. Start FastAPI server on port 8000.")

    uploaded_file = st.file_uploader("Upload Log File (.log, .txt)", type=["log", "txt"])
    
    if uploaded_file is not None:
        if st.button("Parse & Load into Engine", use_container_width=True):
            with st.spinner("Parsing logs via Regex..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
                try:
                    res = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                    if res.status_code == 200:
                        st.success(f"Loaded {res.json().get('records_count')} records!")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    st.markdown("---")
    st.header("🔎 Query Filters")
    filter_level = st.selectbox("Log Level", ["ALL", "ERROR", "CRITICAL", "WARNING", "INFO", "DEBUG"])
    filter_source = st.selectbox(
        "Service Source",
        ["ALL", "auth_service", "payment_gateway", "order_api", "user_service", "db_pool", "notification_worker"]
    )
    search_keyword = st.text_input("Substring Search", placeholder="e.g. timeout, 5000ms, user_id")
    row_limit = st.slider("Max Display Records", min_value=25, max_value=500, value=100, step=25)


# ----------------- MAIN DASHBOARD -----------------
if not backend_info or backend_info.get("active_dataset_rows", 0) == 0:
    st.info("👈 Upload a log file (or `sample_logs/app.log`) from the sidebar to generate analytics.")
    st.stop()

# 1. Fetch Analytics from FastAPI
try:
    summary_res = requests.get(f"{API_BASE_URL}/api/analytics/summary").json()
    dist_res = requests.get(f"{API_BASE_URL}/api/analytics/distributions").json()
    clusters_res = requests.get(f"{API_BASE_URL}/api/analytics/error-clusters?top_n=5").json()
    timeline_res = requests.get(f"{API_BASE_URL}/api/analytics/timeline?interval=1h").json()
except Exception as e:
    st.error(f"Failed to fetch data from API: {str(e)}")
    st.stop()

# 2. Top-level KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Events", f"{summary_res['total_volume']:,}")
kpi2.metric("Total Errors", f"{summary_res['error_count']:,}", delta=f"{summary_res['error_rate_pct']}% Rate", delta_color="inverse")
kpi3.metric("Warnings", f"{summary_res['warning_count']:,}")
kpi4.metric("Info Logs", f"{summary_res['info_count']:,}")

st.markdown("---")

# 3. Visual Charts
tab_overview, tab_clusters, tab_explorer = st.tabs(["📊 Analytics Overview", "🧩 Root Cause Clusters", "📜 Log Search & Explorer"])

with tab_overview:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Errors by Service Source")
        err_dist = dist_res.get("source_error_distribution", {})
        if err_dist:
            df_err = pd.DataFrame(list(err_dist.items()), columns=["Service", "Errors"])
            fig_err = px.bar(df_err, x="Service", y="Errors", color="Errors", color_continuous_scale="Reds")
            fig_err.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_err, use_container_width=True)
        else:
            st.info("No error occurrences found.")

    with col2:
        st.subheader("Log Level Breakdown")
        level_dist = dist_res.get("level_distribution", {})
        if level_dist:
            df_level = pd.DataFrame(list(level_dist.items()), columns=["Level", "Count"])
            fig_pie = px.pie(df_level, names="Level", values="Count", hole=0.4,
                             color="Level",
                             color_discrete_map={"INFO": "#3366cc", "DEBUG": "#6c757d", "WARNING": "#ff9900", "ERROR": "#dc3912", "CRITICAL": "#990099"})
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Event Volume Timeline (Hourly)")
    if timeline_res:
        df_time = pd.DataFrame(timeline_res)
        fig_time = px.line(df_time, x="timestamp", y=["total_events", "error_events"],
                           labels={"value": "Volume", "timestamp": "Timestamp", "variable": "Metric"},
                           color_discrete_map={"total_events": "#2ca02c", "error_events": "#d62728"})
        fig_time.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_time, use_container_width=True)

with tab_clusters:
    st.subheader("Frequent Root Cause Patterns")
    st.caption("Normalized by stripping dynamic numbers, session IDs, and host addresses.")
    if clusters_res:
        df_clusters = pd.DataFrame(clusters_res)
        df_clusters.columns = ["Error Type", "Normalized Pattern", "Originating Source", "Occurrences"]
        st.dataframe(df_clusters, use_container_width=True, hide_index=True)
    else:
        st.info("No recurring error clusters detected.")

with tab_explorer:
    st.subheader("Filtered Log Entries")
    
    # Fetch filtered logs via API
    params = {
        "level": filter_level,
        "source": filter_source,
        "search": search_keyword,
        "limit": row_limit
    }
    log_res = requests.get(f"{API_BASE_URL}/api/logs", params=params).json()
    
    st.caption(f"Showing **{len(log_res.get('logs', []))}** of **{log_res.get('total', 0)}** matching records")
    
    if log_res.get("logs"):
        logs_df = pd.DataFrame(log_res["logs"])
        st.dataframe(
            logs_df[["timestamp", "level", "source", "error_type", "message"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No log entries match your criteria.")
        
    summary_res = requests.get(
    f"{API_BASE_URL}/api/analytics/summary",
    params={"level": filter_level, "source": filter_source}
    ).json()