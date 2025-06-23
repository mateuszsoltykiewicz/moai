"""
Prometheus metrics for UtilsManager (optional).
"""

from prometheus_client import Counter

UTILS_OPERATIONS = Counter(
    "utils_manager_operations_total",
    "Total operations performed by UtilsManager",
    ["operation"]
)

def record_utils_operation(operation: str):
    UTILS_OPERATIONS.labels(operation=operation).inc()
