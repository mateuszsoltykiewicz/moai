"""
Prometheus metrics for ApiManager (optional).
"""

from prometheus_client import Counter

API_OPERATIONS = Counter(
    "api_manager_operations_total",
    "Total operations performed by ApiManager",
    ["operation"]
)

def record_api_operation(operation: str):
    API_OPERATIONS.labels(operation=operation).inc()
