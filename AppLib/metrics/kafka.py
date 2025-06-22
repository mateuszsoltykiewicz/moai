from prometheus_client import Counter, Histogram

KAFKA_OPERATIONS = Counter(
    "kafka_operations_total",
    "Total Kafka operations by type",
    ["operation"]
)

KAFKA_OPERATION_DURATION = Histogram(
    "kafka_operation_duration_seconds",
    "Duration of Kafka operations by type",
    ["operation"]
)

def record_kafka_operation(operation: str, duration: float, count: int = 0):
    KAFKA_OPERATIONS.labels(operation=operation).inc()
    KAFKA_OPERATION_DURATION.labels(operation=operation).observe(duration)
    if count > 0:
        KAFKA_OPERATIONS.labels(operation=f"{operation}_messages").inc(count)
