from prometheus_client import Counter, Histogram

I2C_OPERATIONS = Counter(
    "i2c_operations_total",
    "Total I2C operations",
    ["operation", "device", "status"]
)

I2C_DURATION = Histogram(
    "i2c_operation_duration_seconds",
    "Duration of I2C operations",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)

def record_i2c_operation(operation: str, device: str, status: str = "success"):
    I2C_OPERATIONS.labels(
        operation=operation,
        device=device,
        status=status
    ).inc()
