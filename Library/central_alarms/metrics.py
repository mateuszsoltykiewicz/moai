from prometheus_client import Counter

CENTRAL_ALARM_OPERATIONS = Counter(
    "central_alarms_registry_operations_total",
    "Total operations performed by CentralAlarmsRegistry",
    ["operation"]
)

def record_central_alarm_operation(operation: str):
    CENTRAL_ALARM_OPERATIONS.labels(operation=operation).inc()
