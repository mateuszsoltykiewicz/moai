# core/metrics.py
from prometheus_client import Counter, Histogram

EVENT_OPERATIONS = Counter(
    "event_operations_total",
    "Total event operations by type",
    ["operation"]
)

EVENT_OPERATION_DURATION = Histogram(
    "event_operation_duration_seconds",
    "Duration of event operations by type",
    ["operation"]
)

def record_event_operation(operation: str, duration: float, count: int = 0):
    EVENT_OPERATIONS.labels(operation=operation).inc()
    EVENT_OPERATION_DURATION.labels(operation=operation).observe(duration)
    if count > 0:
        EVENT_OPERATIONS.labels(operation=f"{operation}_items").inc(count)
