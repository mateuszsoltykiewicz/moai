import json
from typing import Dict, Any, Callable, Awaitable, Optional
from .registry import event_registry
from .metrics import record_event_published, record_event_consumed
from .exceptions import EventValidationError

class EventBus:
    def __init__(self, kafka_producer, kafka_consumer_factory, topic_prefix=""):
        self.producer = kafka_producer
        self.consumer_factory = kafka_consumer_factory
        self.topic_prefix = topic_prefix

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        # Validate payload against schema
        schema_cls = event_registry.get(event_type)
        if not schema_cls:
            raise EventValidationError(f"Unknown event type: {event_type}")
        event = schema_cls(**payload)
        topic = f"{self.topic_prefix}{event_type.lower()}"
        await self.producer.send_and_wait(
            topic,
            value=json.dumps(event.dict()).encode("utf-8"),
            key=event_type.encode("utf-8")
        )
        record_event_published(event_type)
    
    async def consume(self, event_type: str, handler: Callable[[BaseModel], Awaitable[None]], group_id: str, batch_size: int = 10):
        schema_cls = event_registry.get(event_type)
        if not schema_cls:
            raise EventValidationError(f"Unknown event type: {event_type}")
        topic = f"{self.topic_prefix}{event_type.lower()}"
        consumer = self.consumer_factory(topic, group_id)
        async for msg in consumer:
            try:
                payload = json.loads(msg.value)
                event = schema_cls(**payload)
                await handler(event)
                record_event_consumed(event_type)
            except Exception as e:
                # Optionally: send to dead-letter topic
                pass
