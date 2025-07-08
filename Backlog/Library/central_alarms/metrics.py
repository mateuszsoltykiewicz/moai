from prometheus_client import Counter, Gauge

CENTRAL_ALARM_OPERATIONS = Counter(
    "central_alarms_operations_total",
    "Total operations performed by CentralAlarmsRegistry",
    ["operation", "status"]
)

ACTIVE_ALARMS_GAUGE = Gauge(
    "central_active_alarms_count",
    "Current count of active alarms"
)

def record_central_alarm_operation(operation: str, status: str = "success"):
    CENTRAL_ALARM_OPERATIONS.labels(operation=operation, status=status).inc()

def update_active_alarms_count(count: int):
    ACTIVE_ALARMS_GAUGE.set(count)
