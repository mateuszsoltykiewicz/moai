import asyncio
import time
from typing import Optional
from .schemas import DisasterStatusResponse
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.events import KafkaProducer, KafkaConsumer
from Library.alarms import AlarmClient
from Library.state import StateClient
from Library.config import ConfigManager

logger = get_logger(__name__)

class DisasterDetectorManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()
    _kafka_producer = KafkaProducer(topic="DisasterDetected")
    _sensor_consumer = KafkaConsumer(topic="sensorData")
    _alarm_client = AlarmClient()
    _state_client = StateClient(service_name="DisasterDetector")
    _disaster_active: bool = False

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        await cls._kafka_producer.connect()
        await cls._state_client.setup()
        await cls.clear_disaster_alarms_on_startup()
        asyncio.create_task(cls._monitor_alarms())
        asyncio.create_task(cls._consume_sensor_data())
        logger.info("DisasterDetectorManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._kafka_producer.disconnect()
        await cls._db.shutdown()
        logger.info("DisasterDetectorManager shutdown complete")

    @classmethod
    async def clear_disaster_alarms_on_startup(cls):
        await cls._alarm_client.clear_alarms(source="DisasterDetector")
        logger.info("Cleared disaster-specific alarms on startup")

    @classmethod
    async def _monitor_alarms(cls):
        """Monitor FATAL alarms and crash if detected."""
        while True:
            fatal_alarm = await cls._alarm_client.get_fatal_alarm()
            if fatal_alarm:
                logger.critical("FATAL alarm detected - stopping DisasterDetector")
                import sys
                sys.exit(1)
            await asyncio.sleep(5)

    @classmethod
    async def _consume_sensor_data(cls):
        """Consume sensorData and detect disasters."""
        async for message in cls._sensor_consumer.listen():
            try:
                data = message["value"]
                if await cls._should_monitor_temperature():
                    if cls._detect_disaster(data):
                        await cls._handle_disaster(data)
            except Exception as e:
                logger.error(f"Sensor data processing error: {e}", exc_info=True)

    @classmethod
    async def _should_monitor_temperature(cls) -> bool:
        # Only monitor if HeatingJob is running (example: check state server)
        heating_state = await cls._state_client.get("HeatingJob:status")
        return heating_state == "running"

    @classmethod
    def _detect_disaster(cls, data: dict) -> bool:
        # Example: disaster if water temperature > 100°C
        return data.get("sensor") == "water_temp" and data.get("value", 0) > 100

    @classmethod
    async def _handle_disaster(cls, data: dict):
        if not cls._disaster_active:
            await cls._kafka_producer.produce({
                "timestamp": time.time(),
                "type": "WATER_OVERHEAT",
                "details": data
            })
            await cls._alarm_client.raise_alarm(
                alarm_id="WATER_OVERHEAT",
                message="Water temperature exceeded safe limit",
                severity="FATAL"
            )
            await cls._state_client.set("DisasterDetected", True)
            cls._disaster_active = True
            logger.critical("Disaster detected and reported!")

    @classmethod
    async def get_disaster_status(cls) -> DisasterStatusResponse:
        status = await cls._state_client.get("DisasterDetected")
        return DisasterStatusResponse(active=bool(status))
