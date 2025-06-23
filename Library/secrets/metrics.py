"""
Prometheus metrics for SecretsManager.
"""

from prometheus_client import Counter

SECRETS_OPERATIONS = Counter(
    "secrets_manager_operations_total",
    "Total operations performed by SecretsManager",
    ["operation"]
)

def record_secrets_operation(operation: str):
    SECRETS_OPERATIONS.labels(operation=operation).inc()
