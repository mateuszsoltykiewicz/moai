from prometheus_client import Counter, Histogram

VAULT_OPERATIONS = Counter(
    "vault_operations_total",
    "Total Vault operations",
    ["operation", "status"]
)

VAULT_LATENCY = Histogram(
    "vault_operation_latency_seconds",
    "Vault operation duration",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_vault_operation(operation: str, status: str = "success"):
    VAULT_OPERATIONS.labels(operation=operation, status=status).inc()

def record_vault_latency(operation: str, duration: float):
    VAULT_LATENCY.labels(operation=operation).observe(duration)

def record_vault_error(operation: str):
    record_vault_operation(operation, "error")
