from prometheus_client import Counter, Histogram

APPSTATE_OPERATIONS = Counter(
    "appstate_operations_total",
    "Total appstate operations",
    ["operation"]
)
APPSTATE_DURATION = Histogram(
    "appstate_operation_duration_seconds",
    "Duration of appstate operations",
    ["operation"]
)

def record_appstate_operation(operation: str, duration: float):
    APPSTATE_OPERATIONS.labels(operation=operation).inc()
    APPSTATE_DURATION.labels(operation=operation).observe(duration)
