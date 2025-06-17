from prometheus_client import Counter, Histogram
from utils.prometheus_instrumentation import REGISTRY

KAFKA_MESSAGES_PRODUCED = Counter(
    "kafka_messages_produced_total",
    "Total Kafka messages produced",
    ["topic"],
    registry=REGISTRY
)
KAFKA_MESSAGES_CONSUMED = Counter(
    "kafka_messages_consumed_total",
    "Total Kafka messages consumed",
    ["topic"],
    registry=REGISTRY
)
KAFKA_ERRORS_TOTAL = Counter(
    "kafka_errors_total",
    "Total Kafka errors",
    ["topic", "error_type"],
    registry=REGISTRY
)
KAFKA_PRODUCE_LATENCY = Histogram(
    "kafka_produce_latency_seconds",
    "Kafka message production latency in seconds",
    ["topic"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5],
    registry=REGISTRY
)

def record_kafka_produced(topic: str):
    KAFKA_MESSAGES_PRODUCED.labels(topic=topic).inc()

def record_kafka_consumed(topic: str):
    KAFKA_MESSAGES_CONSUMED.labels(topic=topic).inc()

def record_kafka_error(topic: str, error_type: str):
    KAFKA_ERRORS_TOTAL.labels(topic=topic, error_type=error_type).inc()

def observe_kafka_latency(topic: str, duration: float):
    KAFKA_PRODUCE_LATENCY.labels(topic=topic).observe(duration)
