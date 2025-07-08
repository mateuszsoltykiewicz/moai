from prometheus_client import Counter

VAULT_OPERATIONS = Counter(
    "vault_operations_total",
    "Total Vault operations",
    ["operation", "status"]
)

def record_vault_operation(operation: str, status: str = "success"):
    VAULT_OPERATIONS.labels(operation=operation, status=status).inc()

def record_vault_error(operation: str):
    record_vault_operation(operation, "error")
