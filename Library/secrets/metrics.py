from prometheus_client import Counter, Histogram

SECRETS_OPERATIONS = Counter(
    "secrets_operations_total",
    "Total secret operations",
    ["operation", "status"]
)

SECRETS_LATENCY = Histogram(
    "secrets_operation_latency_seconds",
    "Secret operation latency",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1.0]
)

def record_secrets_operation(operation: str, status: str = "success"):
    SECRETS_OPERATIONS.labels(operation=operation, status=status).inc()

def record_secrets_latency(operation: str, latency: float):
    SECRETS_LATENCY.labels(operation=operation).observe(latency)

def record_secrets_error(operation: str, error_type: str):
    record_secrets_operation(operation, f"error:{error_type}")
