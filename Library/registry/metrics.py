from prometheus_client import Counter, Gauge

REGISTRY_OPERATIONS = Counter(
    "service_registry_operations_total",
    "Total operations performed by ServiceRegistry",
    ["operation"]
)

REGISTERED_INSTANCES = Gauge(
    "service_registry_registered_instances",
    "Number of registered service instances",
    ["service_name"]
)

def record_registry_operation(operation: str):
    REGISTRY_OPERATIONS.labels(operation=operation).inc()

def update_registered_instances(service_name: str, count: int):
    REGISTERED_INSTANCES.labels(service_name=service_name).set(count)
