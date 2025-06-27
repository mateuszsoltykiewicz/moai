"""
Prometheus metrics for UtilsManager.
"""

from prometheus_client import Counter, Gauge

UTILS_OPERATIONS = Counter(
    "utils_manager_operations_total",
    "Total operations performed by UtilsManager",
    ["operation"]
)

LOG_ROTATIONS = Counter(
    "utils_log_rotations_total",
    "Number of log file rotations"
)

def record_utils_operation(operation: str):
    UTILS_OPERATIONS.labels(operation=operation).inc()

def record_log_rotation():
    LOG_ROTATIONS.inc()
