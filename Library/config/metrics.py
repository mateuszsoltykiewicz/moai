"""
Prometheus metrics for ConfigManager.
"""

from prometheus_client import Counter

CONFIG_OPERATIONS = Counter(
    "config_manager_operations_total",
    "Total operations performed by ConfigManager",
    ["operation"]
)

def record_config_operation(operation: str):
    CONFIG_OPERATIONS.labels(operation=operation).inc()
