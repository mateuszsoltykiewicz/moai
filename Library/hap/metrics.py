from prometheus_client import Counter, Gauge

HAP_OPERATIONS = Counter(
    "hap_operations_total",
    "Total HAP operations",
    ["operation"]
)

ACCESSORY_STATUS = Gauge(
    "hap_accessory_status",
    "Accessory status (1=ok, 0=error)",
    ["accessory"]
)

def record_hap_operation(operation: str):
    HAP_OPERATIONS.labels(operation=operation).inc()

def record_accessory_status(accessory: str, status: int):
    ACCESSORY_STATUS.labels(accessory=accessory).set(status)
