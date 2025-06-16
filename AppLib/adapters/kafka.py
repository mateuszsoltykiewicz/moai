import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
import time

from core.config import AsyncConfigManager
from core.logging import get_logger
from metrics.kafka import (
    KAFKA_MESSAGES_SENT,
    KAFKA_MESSAGES_RECEIVED,
    KAFKA_ERRORS,
    KAFKA_PRODUCE_TIME,
    KAFKA_CONSUMER_LAG
)

logger = get_logger(__name__)

class KafkaAdapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumer: Optional[AIOKafkaConsumer] = None

    @asynccontextmanager
    async def producer_context(self) -> AsyncIterator[AIOKafkaProducer]:
        """Async context manager for Kafka producer"""
        config = await self.config_manager.get()
        self._producer = AIOKafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            security_protocol=config.kafka.security_protocol,
            ssl_context=config.kafka.ssl_context,
            acks=config.kafka.producer_acks
        )
        try:
            await self._producer.start()
            yield self._producer
        except KafkaError as e:
            KAFKA_ERRORS.labels(type="producer").inc()
            logger.error(f"Kafka producer error: {str(e)}")
            raise
        finally:
            await self._producer.stop()

    @asynccontextmanager
    async def consumer_context(self, topic: str, group_id: str) -> AsyncIterator[AIOKafkaConsumer]:
        """Async context manager for Kafka consumer"""
        config = await self.config_manager.get()
        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=config.kafka.bootstrap_servers,
            group_id=group_id,
            security_protocol=config.kafka.security_protocol,
            ssl_context=config.kafka.ssl_context,
            enable_auto_commit=config.kafka.enable_auto_commit
        )
        try:
            await self._consumer.start()
            yield self._consumer
        except KafkaError as e:
            KAFKA_ERRORS.labels(type="consumer").inc()
            logger.error(f"Kafka consumer error: {str(e)}")
            raise
        finally:
            await self._consumer.stop()

    async def produce(self, topic: str, value: bytes, key: Optional[bytes] = None) -> None:
        """Produce a message to Kafka with metrics"""
        start = time.monotonic()
        try:
            async with self.producer_context() as producer:
                await producer.send(topic, value=value, key=key)
                KAFKA_MESSAGES_SENT.inc()
                KAFKA_PRODUCE_TIME.observe(time.monotonic() - start)
        except Exception as e:
            KAFKA_ERRORS.labels(type="produce").inc()
            raise

    async def consume(self, topic: str, group_id: str) -> AsyncIterator[Dict[str, Any]]:
        """Consume messages from Kafka with metrics"""
        async with self.consumer_context(topic, group_id) as consumer:
            async for msg in consumer:
                KAFKA_MESSAGES_RECEIVED.inc()
                KAFKA_CONSUMER_LAG.set(consumer.end_offsets()[msg.partition] - msg.offset)
                yield {
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "key": msg.key,
                    "value": msg.value,
                    "timestamp": msg.timestamp
                }
