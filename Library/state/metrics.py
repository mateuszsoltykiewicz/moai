from prometheus_client import Counter, Histogram

STATE_OPERATIONS = Counter(
    "state_operations_total",
    "Total state operations",
    ["operation", "status"]
)

STATE_LATENCY = Histogram(
    "state_operation_latency_seconds",
    "State operation duration",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_state_operation(operation: str, status: str = "success"):
    STATE_OPERATIONS.labels(operation=operation, status=status).inc()

def record_state_latency(operation: str, latency: float):
    STATE_LATENCY.labels(operation=operation).observe(latency)

def record_state_error(operation: str, error_type: str):
    record_state_operation(operation, f"error:{error_type}")
