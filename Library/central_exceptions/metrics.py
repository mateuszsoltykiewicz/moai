from prometheus_client import Counter

EXCEPTIONS_OPERATIONS = Counter(
    "central_exceptions_operations_total",
    "Total operations performed by CentralExceptionsManager",
    ["operation"]
)

def record_exceptions_operation(operation: str):
    EXCEPTIONS_OPERATIONS.labels(operation=operation).inc()
