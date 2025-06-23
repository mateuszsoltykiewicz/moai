"""
Prometheus metrics for AdapterManager.
"""

from prometheus_client import Counter

ADAPTER_OPERATIONS = Counter(
    "adapter_manager_operations_total",
    "Total operations performed by AdapterManager",
    ["operation"]
)

def record_adapter_operation(operation: str):
    ADAPTER_OPERATIONS.labels(operation=operation).inc()
