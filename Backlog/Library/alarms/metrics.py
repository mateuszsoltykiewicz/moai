"""
Prometheus metrics for AlarmsManager.
"""

from prometheus_client import Counter

ALARM_OPERATIONS = Counter(
    "alarms_manager_operations_total",
    "Total operations performed by AlarmsManager",
    ["operation"]
)

def record_alarm_operation(operation: str):
    ALARM_OPERATIONS.labels(operation=operation).inc()
