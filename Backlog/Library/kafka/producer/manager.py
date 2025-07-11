import asyncio
from aiokafka import AIOKafkaProducer
from typing import Dict, Any
from kafka.exceptions import KafkaError
from kafka.metrics import record_kafka_operation
from Library.logging import get_logger
from .schemas import KafkaProduceRequest

logger = get_logger(__name__)

class KafkaProducerManager:
    def __init__(self, config: Dict[str, Any]):
        self._producer: AIOKafkaProducer = None
        self._bootstrap_servers = config.get("bootstrap_servers", "localhost:9092")
        self._acks = config.get("acks", "all")
        self._max_batch_size = config.get("max_batch_size", 16384)
        self._message_timeout = config.get("message_timeout", 30000)

    async def setup(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            acks=self._acks,
            compression_type="gzip",
            max_batch_size=self._max_batch_size,
            linger_ms=20,
            request_timeout_ms=self._message_timeout
        )
        await self._producer.start()
        logger.info("Producer started")

    async def shutdown(self):
        if self._producer:
            await self._producer.stop()
            logger.info("Producer stopped")

    async def produce(self, req: KafkaProduceRequest):
        try:
            await self._producer.send_and_wait(
                req.topic,
                value=req.value.encode("utf-8"),
                key=req.key.encode("utf-8") if req.key else None,
                headers=req.headers
            )
            record_kafka_operation("produce", req.topic, "success")
            logger.info(f"Produced message to {req.topic}")
        except Exception as e:
            record_kafka_operation("produce", req.topic, "failed")
            logger.error(f"Kafka produce error: {e}", exc_info=True)
            raise KafkaError(f"Produce error: {e}") from e
