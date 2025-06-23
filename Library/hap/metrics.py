"""
Prometheus metrics for HAPManager.
"""

from prometheus_client import Counter

HAP_OPERATIONS = Counter(
    "hap_manager_operations_total",
    "Total operations performed by HAPManager",
    ["operation"]
)

def record_hap_operation(operation: str):
    HAP_OPERATIONS.labels(operation=operation).inc()
