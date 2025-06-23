"""
Prometheus metrics for VaultManager.
"""

from prometheus_client import Counter

VAULT_OPERATIONS = Counter(
    "vault_manager_operations_total",
    "Total operations performed by VaultManager",
    ["operation"]
)

def record_vault_operation(operation: str):
    VAULT_OPERATIONS.labels(operation=operation).inc()
