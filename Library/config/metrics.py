from prometheus_client import Counter, Histogram

CONFIG_OPERATIONS = Counter(
    "config_manager_operations_total",
    "Total config operations",
    ["operation"]
)

CONFIG_ERRORS = Counter(
    "config_manager_errors_total",
    "Total configuration errors",
    ["error_type"]
)

def record_config_operation(operation: str):
    CONFIG_OPERATIONS.labels(operation=operation).inc()

def record_config_error(error_type: str = "validation"):
    CONFIG_ERRORS.labels(error_type=error_type).inc()
