from prometheus_client import Counter, Histogram

I2C_OPERATIONS = Counter(
    "i2c_operations_total",
    "Total I2C operations by type",
    ["operation"]
)

I2C_OPERATION_DURATION = Histogram(
    "i2c_operation_duration_seconds",
    "Duration of I2C operations by type",
    ["operation"]
)

def record_i2c_operation(operation: str, duration: float):
    I2C_OPERATIONS.labels(operation=operation).inc()
    I2C_OPERATION_DURATION.labels(operation=operation).observe(duration)
