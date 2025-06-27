import asyncio
from aiokafka import AIOKafkaConsumer
from typing import Dict, Any, List
from kafka.exceptions import KafkaError
from kafka.metrics import record_kafka_operation
from kafka.utils import log_info
from .schemas import KafkaConsumeResponse

class KafkaConsumerManager:
    def __init__(self, config: Dict[str, Any]):
        self._consumers: Dict[str, AIOKafkaConsumer] = {}
        self._bootstrap_servers = config.get("bootstrap_servers", "localhost:9092")
        self._session_timeout = config.get("session_timeout", 30000)
        self._max_poll_interval = config.get("max_poll_interval", 300000)
        self._lock = asyncio.Lock()
        self._consumer_timeout = config.get("consumer_timeout", 5000)

    async def shutdown(self):
        async with self._lock:
            for consumer in self._consumers.values():
                await consumer.stop()
            self._consumers.clear()
            log_info("KafkaConsumerManager: All consumers stopped")

    async def consume(self, topic: str, group_id: str, limit: int = 100) -> List[KafkaConsumeResponse]:
        consumer_key = f"{topic}-{group_id}"
        
        async with self._lock:
            consumer = self._consumers.get(consumer_key)
            if not consumer:
                consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=self._bootstrap_servers,
                    group_id=group_id,
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                    session_timeout_ms=self._session_timeout,
                    max_poll_interval_ms=self._max_poll_interval
                )
                await consumer.start()
                self._consumers[consumer_key] = consumer
                log_info(f"Consumer started for {topic} in group {group_id}")

        messages = []
        try:
            while len(messages) < limit:
                batch = await consumer.getmany(timeout_ms=self._consumer_timeout, max_records=limit)
                for tp, msgs in batch.items():
                    for msg in msgs:
                        messages.append(KafkaConsumeResponse(
                            topic=msg.topic,
                            key=msg.key.decode("utf-8") if msg.key else None,
                            value=msg.value.decode("utf-8"),
                            partition=msg.partition,
                            offset=msg.offset,
                            timestamp=msg.timestamp,
                            headers=dict(msg.headers) if msg.headers else None
                        ))
                        if len(messages) >= limit:
                            break
                if not batch:
                    break
            
            await consumer.commit()
            record_kafka_operation("consume", topic, "success")
            log_info(f"Consumed {len(messages)} messages from {topic}")
            return messages
        except Exception as e:
            record_kafka_operation("consume", topic, "failed")
            raise KafkaError(f"Consume error: {e}") from e
