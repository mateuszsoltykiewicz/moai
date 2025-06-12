from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource, ConfigResourceType
from core.config import AsyncConfigManager

_kafka_producer = None

async def get_kafka_producer():
    global _kafka_producer
    if _kafka_producer is None:
        config = await AsyncConfigManager.get()
        _kafka_producer = AIOKafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers
        )
        await _kafka_producer.start()
    return _kafka_producer

async def get_kafka_consumer(
    topic: str, group_id: str, auto_commit: bool = True, offset_reset: str = "latest"
):
    config = await AsyncConfigManager.get()
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=auto_commit,
        auto_offset_reset=offset_reset
    )
    await consumer.start()
    return consumer

def get_admin_client():
    # Synchronous for topic management
    config = AsyncConfigManager.get_sync()
    return AdminClient({'bootstrap.servers': config.kafka.bootstrap_servers})
