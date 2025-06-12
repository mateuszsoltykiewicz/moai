from prometheus_client import Counter

KAFKA_MESSAGES_PRODUCED = Counter(
    "kafka_messages_produced_total", "Total Kafka messages produced", ["topic"]
)
KAFKA_MESSAGES_CONSUMED = Counter(
    "kafka_messages_consumed_total", "Total Kafka messages consumed", ["topic"]
)
KAFKA_ERRORS_TOTAL = Counter(
    "kafka_errors_total", "Total Kafka errors", ["topic"]
)
