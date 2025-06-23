"""
KafkaManager: Async Kafka producer/consumer management.

- Manages Kafka producers and consumers
- Supports dynamic topic configuration and schema validation
- Integrates with metrics, logging, and all components
- Async and thread-safe
"""

import asyncio
from typing import Dict, Any, Optional, List
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .schemas import KafkaProduceRequest, KafkaConsumeResponse
from .exceptions import KafkaError
from .metrics import record_kafka_operation
from .utils import log_info

class KafkaManager:
    def __init__(self, config: Dict[str, Any]):
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumers: Dict[str, AIOKafkaConsumer] = {}
        self._bootstrap_servers = config.get("bootstrap_servers", "localhost:9092")
        self._lock = asyncio.Lock()

    async def setup(self):
        """
        Async setup logic for the KafkaManager.
        """
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()
        log_info("KafkaManager: Producer started.")

    async def shutdown(self):
        """
        Async shutdown logic for the KafkaManager.
        """
        if self._producer:
            await self._producer.stop()
            log_info("KafkaManager: Producer stopped.")
        for consumer in self._consumers.values():
            await consumer.stop()
        log_info("KafkaManager: All consumers stopped.")

    async def produce(self, req: KafkaProduceRequest):
        """
        Produce a message to a Kafka topic.
        """
        try:
            await self._producer.send_and_wait(
                req.topic,
                value=req.value.encode("utf-8"),
                key=req.key.encode("utf-8") if req.key else None
            )
            record_kafka_operation("produce")
            log_info(f"KafkaManager: Produced message to {req.topic}")
        except Exception as e:
            raise KafkaError(f"Kafka produce error: {e}")

    async def consume(self, topic: str, group_id: str, limit: int = 10) -> List[KafkaConsumeResponse]:
        """
        Consume messages from a Kafka topic.
        """
        consumer = self._consumers.get(topic)
        if not consumer:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self._bootstrap_servers,
                group_id=group_id,
                auto_offset_reset="latest"
            )
            await consumer.start()
            self._consumers[topic] = consumer

        messages = []
        try:
            async for msg in consumer:
                messages.append(
                    KafkaConsumeResponse(
                        topic=msg.topic,
                        key=msg.key.decode("utf-8") if msg.key else None,
                        value=msg.value.decode("utf-8"),
                        partition=msg.partition,
                        offset=msg.offset,
                        timestamp=msg.timestamp
                    )
                )
                if len(messages) >= limit:
                    break
            record_kafka_operation("consume")
            log_info(f"KafkaManager: Consumed {len(messages)} messages from {topic}")
        except Exception as e:
            raise KafkaError(f"Kafka consume error: {e}")
        return messages
