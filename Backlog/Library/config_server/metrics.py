from prometheus_client import Counter, Histogram

CONFIG_OPERATIONS = Counter(
    "config_server_operations_total",
    "Total operations performed by ConfigServer",
    ["operation"]
)

CONFIG_FETCH_TIME = Histogram(
    "config_fetch_duration_seconds",
    "Time taken to fetch configuration",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_config_operation(operation: str):
    CONFIG_OPERATIONS.labels(operation=operation).inc()
