from typing import Dict, Any
from .exceptions import StateSyncError
from tenacity import retry, stop_after_attempt, wait_exponential

class KafkaStatePublisher:
    def __init__(self, kafka_manager):
        self._kafka_manager = kafka_manager

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def publish_state(self, service_name: str, state: Dict[str, Any]):
        try:
            await self._kafka_manager.produce(
                topic="state_events",
                key=service_name,
                value=state,
                headers={"idempotency_key": "state_update"}
            )
        except Exception as e:
            raise StateSyncError(f"Kafka publish error: {e}")
