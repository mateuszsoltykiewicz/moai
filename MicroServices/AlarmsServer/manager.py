import asyncio
import time
from typing import List, Dict, Optional
from .schemas import AlarmCreateRequest, AlarmDeleteRequest, AlarmResponse
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.state import StateClient
from Library.events import KafkaConsumer
from Library.alarms import AlarmClient

logger = get_logger(__name__)

class AlarmsManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()
    _state_client = StateClient(service_name="AlarmsServer")
    _kafka_consumer = KafkaConsumer(topic="createAlarm")

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        await cls._state_client.setup()
        # Start Kafka consumer in background
        asyncio.create_task(cls._consume_create_alarms())
        logger.info("AlarmsManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._db.shutdown()
        await cls._state_client.shutdown()
        logger.info("AlarmsManager shutdown complete")

    @classmethod
    async def create_alarm(cls, req: AlarmCreateRequest) -> AlarmResponse:
        async with cls._lock:
            # Insert alarm into DB
            await cls._db.create_record("alarms", req.dict())
            # Add to state
            await cls._state_client.set(f"alarm:{req.id}", req.dict())
            logger.info(f"Created alarm {req.id}")
            return AlarmResponse(**req.dict())

    @classmethod
    async def delete_alarm(cls, req: AlarmDeleteRequest) -> AlarmResponse:
        async with cls._lock:
            # Mark alarm as inactive (soft delete)
            record = await cls._db.get_record("alarms", req.id)
            if not record:
                raise Exception(f"Alarm {req.id} not found")
            record["active"] = False
            await cls._db.update_record("alarms", req.id, record)
            # Update state
            await cls._state_client.set(f"alarm:{req.id}", record)
            logger.info(f"Deleted (soft) alarm {req.id}")
            return AlarmResponse(**record)

    @classmethod
    async def get_current_alarms(cls) -> List[AlarmResponse]:
        async with cls._lock:
            records = await cls._db.query_records("alarms", filters={"active": True})
            return [AlarmResponse(**r) for r in records]

    @classmethod
    async def _consume_create_alarms(cls):
        async for message in cls._kafka_consumer.listen():
            try:
                alarm_data = message["value"]
                await cls.create_alarm(AlarmCreateRequest(**alarm_data))
            except Exception as e:
                logger.error(f"Failed to process createAlarm message: {e}", exc_info=True)
