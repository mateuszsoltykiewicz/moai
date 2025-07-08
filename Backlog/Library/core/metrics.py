"""
Prometheus metrics for CoreManager.
"""

from prometheus_client import Counter

CORE_OPERATIONS = Counter(
    "core_manager_operations_total",
    "Total operations performed by CoreManager",
    ["operation"]
)

def record_core_operation(operation: str):
    CORE_OPERATIONS.labels(operation=operation).inc()
