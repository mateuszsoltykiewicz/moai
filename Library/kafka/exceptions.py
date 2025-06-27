class KafkaError(Exception):
    """Base Kafka error"""
    pass

class KafkaProducerError(KafkaError):
    """Producer-specific error"""
    pass

class KafkaConsumerError(KafkaError):
    """Consumer-specific error"""
    pass

class KafkaConnectionError(KafkaError):
    """Connection-related error"""
    pass
