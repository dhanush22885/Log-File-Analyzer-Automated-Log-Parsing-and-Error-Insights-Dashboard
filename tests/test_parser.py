import pytest
import pandas as pd
from backend.parser import parse_log_line, parse_logs_to_dataframe
from backend.analytics import compute_summary_metrics, normalize_error_message, compute_error_clusters

SAMPLE_LOG_DATA = """2026-09-28 10:00:00 [INFO] [auth_service] User 123 logged in successfully.
2026-09-28 10:01:00 [WARNING] [db_pool] Slow query detected: 1450ms execution time.
2026-09-28 10:02:00 [ERROR] [payment_gateway] PaymentGatewayTimeout: Stripe API call exceeded 5000ms threshold.
2026-09-28 10:03:00 [ERROR] [payment_gateway] PaymentGatewayTimeout: Stripe API call exceeded 5000ms threshold.
"""

def test_parse_valid_log_line():
    line = "2026-09-28 12:00:00 [ERROR] [auth_service] DatabaseConnectionError: Connection refused."
    parsed = parse_log_line(line)
    
    assert parsed is not None
    assert parsed["timestamp"] == "2026-09-28 12:00:00"
    assert parsed["level"] == "ERROR"
    assert parsed["source"] == "auth_service"
    assert parsed["error_type"] == "DatabaseConnectionError"

def test_normalize_pattern():
    raw_error = "User 984 failed authentication from IP 192.168.1.45 after 300ms"
    normalized = normalize_error_message(raw_error)
    assert "<VAL>" in normalized
    assert "<IP>" in normalized
    assert "984" not in normalized
    assert "192.168.1.45" not in normalized

def test_dataframe_and_metrics():
    df = parse_logs_to_dataframe(SAMPLE_LOG_DATA)
    assert len(df) == 4
    
    metrics = compute_summary_metrics(df)
    assert metrics["total_volume"] == 4
    assert metrics["error_count"] == 2
    assert metrics["warning_count"] == 1
    assert metrics["error_rate_pct"] == 50.0

def test_error_clustering():
    df = parse_logs_to_dataframe(SAMPLE_LOG_DATA)
    clusters = compute_error_clusters(df, top_n=1)
    
    assert len(clusters) == 1
    assert clusters[0]["error_type"] == "PaymentGatewayTimeout"
    assert clusters[0]["occurrence_count"] == 2