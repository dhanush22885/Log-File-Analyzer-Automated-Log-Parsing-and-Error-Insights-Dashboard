import os
import random
from datetime import datetime, timedelta

LOG_LEVELS = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
LEVEL_WEIGHTS = [0.60, 0.15, 0.12, 0.10, 0.03]  # Skewed toward realistic distributions

SOURCES = [
    "auth_service",
    "payment_gateway",
    "order_api",
    "user_service",
    "db_pool",
    "notification_worker"
]

MESSAGES = {
    "INFO": [
        "User {user_id} logged in successfully.",
        "Order #{order_id} placed. Total: ${amount}.",
        "Health check probe passed in {latency}ms.",
        "Notification dispatched to user {user_id}.",
        "Database connection acquired from pool.",
        "Token refreshed for session {session_id}."
    ],
    "DEBUG": [
        "Payload verification completed for request #{req_id}.",
        "Cache hit for key 'session:{session_id}'.",
        "Executing query: SELECT * FROM users WHERE id = {user_id};",
        "Connection pool active connections: {pool_count}."
    ],
    "WARNING": [
        "High memory consumption detected: {mem_pct}% used.",
        "Slow query detected: {latency}ms execution time.",
        "Rate limit threshold reached for IP 192.168.1.{ip_suffix}.",
        "Deprecated API endpoint accessed: /v1/checkout."
    ],
    "ERROR": [
        "DatabaseConnectionError: Failed to connect to host db-replica-1:5432.",
        "PaymentGatewayTimeout: Stripe API call exceeded 5000ms threshold.",
        "KeyError: 'user_id' not found in incoming request payload.",
        "AuthenticationFailed: Invalid JWT signature for user {user_id}.",
        "FileNotFoundError: Template /app/templates/receipt.html not found.",
        "IntegrityError: Duplicate key value violates unique constraint 'users_email_key'."
    ],
    "CRITICAL": [
        "OutOfMemoryError: Container worker-2 killed by OOM killer.",
        "DeadlockDetected: Transaction aborted on table 'orders'.",
        "ServiceUnavailable: Downstream auth cluster unreachable."
    ]
}

def generate_log_file(filename="sample_logs/app.log", total_lines=2500):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    base_time = datetime.now() - timedelta(hours=24)
    current_time = base_time

    with open(filename, "w", encoding="utf-8") as f:
        for _ in range(total_lines):
            current_time += timedelta(seconds=random.randint(1, 45))
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            level = random.choices(LOG_LEVELS, weights=LEVEL_WEIGHTS)[0]
            source = random.choice(SOURCES)
            
            raw_msg = random.choice(MESSAGES[level])
            message = raw_msg.format(
                user_id=random.randint(100, 999),
                order_id=random.randint(10000, 99999),
                amount=f"{random.uniform(10.0, 500.0):.2f}",
                latency=random.randint(120, 2400),
                session_id=random.randint(1000, 9999),
                req_id=random.randint(50000, 99999),
                pool_count=random.randint(5, 50),
                mem_pct=random.randint(82, 98),
                ip_suffix=random.randint(2, 254)
            )

            # Standard structured log format:
            # 2026-09-28 12:45:10 [ERROR] [payment_gateway] PaymentGatewayTimeout: Stripe API call exceeded 5000ms threshold.
            log_line = f"{timestamp} [{level}] [{source}] {message}\n"
            f.write(log_line)

    print(f"Successfully generated {total_lines} sample log entries at: {filename}")

if __name__ == "__main__":
    generate_log_file()