from prometheus_client import Counter, Gauge

STATE_OPERATIONS = Counter(
    "central_state_operations_total",
    "Total operations performed by CentralStateRegistry",
    ["operation"]
)

SERVICE_COUNT = Gauge(
    "central_state_services_count",
    "Current count of registered services"
)

def record_state_operation(operation: str):
    STATE_OPERATIONS.labels(operation=operation).inc()

def update_service_count(count: int):
    SERVICE_COUNT.set(count)
