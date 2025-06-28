import json
from typing import Dict, Any, Callable, Awaitable
from .registry import event_registry
from .metrics import record_event_published, record_event_consumed
from .exceptions import EventValidationError, EventBusError
from Library.logging import get_logger

logger = get_logger(__name__)

class EventBus:
    def __init__(self, kafka_producer, kafka_consumer_factory, topic_prefix=""):
        self.producer = kafka_producer
        self.consumer_factory = kafka_consumer_factory
        self.topic_prefix = topic_prefix

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        try:
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
            logger.info(f"Published {event_type} event to {topic}")
            
        except Exception as e:
            logger.error(f"Event publish failed: {event_type} - {e}", exc_info=True)
            raise EventBusError(f"Publish failed: {str(e)}") from e
    
    async def consume(self, event_type: str, handler: Callable[[Any], Awaitable[None]], group_id: str, batch_size: int = 10):
        try:
            schema_cls = event_registry.get(event_type)
            if not schema_cls:
                raise EventValidationError(f"Unknown event type: {event_type}")
                
            topic = f"{self.topic_prefix}{event_type.lower()}"
            consumer = self.consumer_factory(topic, group_id)
            logger.info(f"Starting consumer for {event_type} in group {group_id}")
            
            async for msg in consumer:
                try:
                    payload = json.loads(msg.value)
                    event = schema_cls(**payload)
                    await handler(event)
                    record_event_consumed(event_type)
                except Exception as e:
                    logger.error(
                        f"Event processing failed: {event_type} - {e}\n"
                        f"Message: {msg.value}", 
                        exc_info=True
                    )
                    # Optionally: send to dead-letter topic
        except Exception as e:
            logger.error(f"Event consumer failed: {event_type} - {e}", exc_info=True)
            raise EventBusError(f"Consume failed: {str(e)}") from e
