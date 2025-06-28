from prometheus_client import Counter

STATE_OPERATIONS = Counter(
    "state_operations_total",
    "Total state operations",
    ["operation", "status"]
)

def record_state_operation(operation: str, status: str = "success"):
    STATE_OPERATIONS.labels(operation=operation, status=status).inc()

def record_state_error(operation: str, error_type: str):
    record_state_operation(operation, f"error:{error_type}")
