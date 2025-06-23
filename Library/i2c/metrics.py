"""
Prometheus metrics for I2CManager.
"""

from prometheus_client import Counter

I2C_OPERATIONS = Counter(
    "i2c_manager_operations_total",
    "Total operations performed by I2CManager",
    ["operation"]
)

def record_i2c_operation(operation: str):
    I2C_OPERATIONS.labels(operation=operation).inc()
