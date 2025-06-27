from prometheus_client import Counter, Histogram

KAFKA_OPERATIONS = Counter(
    "kafka_operations_total",
    "Total Kafka operations",
    ["operation", "topic", "status"]
)

KAFKA_LATENCY = Histogram(
    "kafka_operation_latency_seconds",
    "Kafka operation latency",
    ["operation", "topic"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_kafka_operation(operation: str, topic: str, status: str = "success"):
    KAFKA_OPERATIONS.labels(
        operation=operation,
        topic=topic,
        status=status
    ).inc()

def record_kafka_latency(operation: str, topic: str, latency: float):
    KAFKA_LATENCY.labels(
        operation=operation,
        topic=topic
    ).observe(latency)
