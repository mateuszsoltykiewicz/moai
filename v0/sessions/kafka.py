"""
Async Kafka Session Manager

- Manages async Kafka producer and consumer lifecycles.
- Provides context manager and explicit start/stop methods.
- Integrates with aiokafka for high-performance async messaging.
"""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Optional, List
import logging

class KafkaSessionManager:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: Optional[str] = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: Optional[str] = None,
        sasl_plain_username: Optional[str] = None,
        sasl_plain_password: Optional[str] = None,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism
        self.sasl_plain_username = sasl_plain_username
        self.sasl_plain_password = sasl_plain_password
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.logger = logging.getLogger("KafkaSessionManager")

    async def start_producer(self) -> AIOKafkaProducer:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            security_protocol=self.security_protocol,
            sasl_mechanism=self.sasl_mechanism,
            sasl_plain_username=self.sasl_plain_username,
            sasl_plain_password=self.sasl_plain_password,
        )
        await self.producer.start()
        self.logger.info("Kafka producer started.")
        return self.producer

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()
            self.logger.info("Kafka producer stopped.")

    async def start_consumer(self, topics: List[str]) -> AIOKafkaConsumer:
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            security_protocol=self.security_protocol,
            sasl_mechanism=self.sasl_mechanism,
            sasl_plain_username=self.sasl_plain_username,
            sasl_plain_password=self.sasl_plain_password,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        self.logger.info(f"Kafka consumer started for topics: {topics}")
        return self.consumer

    async def stop_consumer(self):
        if self.consumer:
            await self.consumer.stop()
            self.logger.info("Kafka consumer stopped.")

    async def __aenter__(self):
        # Optionally start producer or consumer here if needed
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop_producer()
        await self.stop_consumer()
