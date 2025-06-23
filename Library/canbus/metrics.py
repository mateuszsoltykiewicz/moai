"""
Prometheus metrics for CanbusManager.
"""

from prometheus_client import Counter

CANBUS_OPERATIONS = Counter(
    "canbus_manager_operations_total",
    "Total operations performed by CanbusManager",
    ["operation"]
)

def record_canbus_operation(operation: str):
    CANBUS_OPERATIONS.labels(operation=operation).inc()
