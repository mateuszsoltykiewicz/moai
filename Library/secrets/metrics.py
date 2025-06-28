from prometheus_client import Counter

SECRETS_OPERATIONS = Counter(
    "secrets_operations_total",
    "Total secret operations",
    ["operation", "status"]
)

def record_secrets_operation(operation: str, status: str = "success"):
    SECRETS_OPERATIONS.labels(operation=operation, status=status).inc()

def record_secrets_error(operation: str, error_type: str):
    record_secrets_operation(operation, f"error:{error_type}")
