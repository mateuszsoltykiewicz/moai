"""
Prometheus metrics for KafkaManager.
"""

from prometheus_client import Counter

KAFKA_OPERATIONS = Counter(
    "kafka_manager_operations_total",
    "Total operations performed by KafkaManager",
    ["operation"]
)

def record_kafka_operation(operation: str):
    KAFKA_OPERATIONS.labels(operation=operation).inc()
