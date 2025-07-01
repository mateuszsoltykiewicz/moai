from prometheus_client import Counter

STATE_OPERATIONS = Counter(
    "state_server_operations_total",
    "Total state operations",
    ["operation"]
)

def record_state_operation(operation: str):
    STATE_OPERATIONS.labels(operation=operation).inc()
