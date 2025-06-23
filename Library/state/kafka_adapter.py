# state/kafka_adapter.py

from typing import Dict, Any
from .exceptions import StateSyncError

class KafkaStatePublisher:
    def __init__(self, kafka_manager):
        self._kafka_manager = kafka_manager

    async def publish_state(self, service_name: str, state: Dict[str, Any]):
        try:
            await self._kafka_manager.produce(
                topic="state_events",
                key=service_name,
                value=state
            )
        except Exception as e:
            raise StateSyncError(f"Kafka publish error: {e}")
