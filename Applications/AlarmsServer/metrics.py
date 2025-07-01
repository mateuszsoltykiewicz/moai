from prometheus_client import Counter

ALARMS_OPERATIONS = Counter(
    "alarms_operations_total",
    "Total alarm operations",
    ["operation"]
)

def record_alarm_operation(operation: str):
    ALARMS_OPERATIONS.labels(operation=operation).inc()
