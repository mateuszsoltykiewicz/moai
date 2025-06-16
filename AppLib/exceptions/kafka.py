from .base import AppLibException

class KafkaException(AppLibException):
    """General Kafka error."""

class KafkaConnectionError(KafkaException):
    """Failed to connect to Kafka broker."""

class KafkaMessageError(KafkaException):
    """Kafka message send/receive failed."""
