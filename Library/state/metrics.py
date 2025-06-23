"""
Prometheus metrics for StateManager.
"""

from prometheus_client import Counter

STATE_OPERATIONS = Counter(
    "state_manager_operations_total",
    "Total operations performed by StateManager",
    ["operation"]
)

def record_state_operation(operation: str):
    STATE_OPERATIONS.labels(operation=operation).inc()
