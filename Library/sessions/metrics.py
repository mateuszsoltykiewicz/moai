"""
Prometheus metrics for SessionsManager.
"""

from prometheus_client import Counter

SESSION_OPERATIONS = Counter(
    "sessions_manager_operations_total",
    "Total operations performed by SessionsManager",
    ["operation"]
)

def record_session_operation(operation: str):
    SESSION_OPERATIONS.labels(operation=operation).inc()
