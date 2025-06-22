from prometheus_client import Counter, Histogram

SECRETS_OPERATIONS = Counter(
    "secrets_operations_total",
    "Total secrets operations by type",
    ["operation"]
)

SECRETS_OPERATION_DURATION = Histogram(
    "secrets_operation_duration_seconds",
    "Duration of secrets operations by type",
    ["operation"]
)

def record_secrets_operation(operation: str, duration: float):
    SECRETS_OPERATIONS.labels(operation=operation).inc()
    SECRETS_OPERATION_DURATION.labels(operation=operation).observe(duration)
