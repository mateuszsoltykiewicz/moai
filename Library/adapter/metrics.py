from prometheus_client import Counter, Histogram

ADAPTER_OPERATIONS = Counter(
    "adapter_manager_operations_total",
    "Total operations performed by AdapterManager",
    ["operation", "adapter_type", "status"]
)

ADAPTER_LATENCY = Histogram(
    "adapter_manager_operation_latency_seconds",
    "Adapter operation latency",
    ["operation", "adapter_type"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_adapter_operation(operation: str, adapter_type: str, status: str = "success"):
    ADAPTER_OPERATIONS.labels(
        operation=operation,
        adapter_type=adapter_type,
        status=status
    ).inc()

def record_adapter_latency(operation: str, adapter_type: str, latency: float):
    ADAPTER_LATENCY.labels(
        operation=operation,
        adapter_type=adapter_type
    ).observe(latency)
