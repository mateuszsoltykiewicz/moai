"""
Prometheus metrics for MtlsManager.
"""

from prometheus_client import Counter

MTLS_OPERATIONS = Counter(
    "mtls_manager_operations_total",
    "Total operations performed by MtlsManager",
    ["operation"]
)

def record_mtls_operation(operation: str):
    MTLS_OPERATIONS.labels(operation=operation).inc()
