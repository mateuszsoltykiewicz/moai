"""
Prometheus metrics for DatabaseManager.
"""

from prometheus_client import Counter

DB_OPERATIONS = Counter(
    "database_manager_operations_total",
    "Total operations performed by DatabaseManager",
    ["operation"]
)

def record_db_operation(operation: str):
    DB_OPERATIONS.labels(operation=operation).inc()
