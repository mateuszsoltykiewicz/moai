# /Python/libraries/core/async_kafka_integration/__init__.py
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

async def get_producer(bootstrap_servers):
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    return producer

async def get_consumer(topic, group_id, bootstrap_servers, **kwargs):
    consumer = AIOKafkaConsumer(
        topic,
        group_id=group_id,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        **kwargs
    )
    await consumer.start()
    return consumer
