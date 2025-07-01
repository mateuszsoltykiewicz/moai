import asyncio
import time
from typing import List, Dict
from .schemas import SensorData, SensorDataResponse
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.events import KafkaProducer
from Library.alarms import AlarmClient
from Library.state import StateClient
from Library.config import ConfigManager

logger = get_logger(__name__)

class CANBusManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()
    _kafka_producer = KafkaProducer(topic="sensorData")
    _alarm_client = AlarmClient()
    _state_client = StateClient(service_name="CANBusAdapter")
    _latest_data: List[SensorData] = []

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        await cls._kafka_producer.connect()
        await cls._state_client.setup()
        await cls.clear_alarms_on_startup()
        asyncio.create_task(cls._poll_canbus())
        logger.info("CANBusManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._kafka_producer.disconnect()
        await cls._db.shutdown()
        logger.info("CANBusManager shutdown complete")

    @classmethod
    async def clear_alarms_on_startup(cls):
        # Clear all CANBus-specific alarms on startup
        await cls._alarm_client.clear_alarms(source="CANBusAdapter")
        logger.info("Cleared CANBus-specific alarms on startup")

    @classmethod
    async def _poll_canbus(cls):
        """Simulate polling CAN bus, producing sensor data and alarms."""
        while True:
            try:
                # Simulate reading from CAN bus hardware
                sensor_data = SensorData(
                    id=f"sensor-{int(time.time())}",
                    value=42.0,  # Replace with actual sensor reading
                    timestamp=time.time(),
                    status="OK"
                )
                await cls._db.create_record("sensor_data", sensor_data.dict())
                await cls._kafka_producer.produce(sensor_data.dict())
                cls._latest_data.append(sensor_data)
                # Simulate alarm condition
                if sensor_data.value > 100:
                    await cls._alarm_client.raise_alarm(
                        alarm_id="CANBUS_OVERLOAD",
                        message="CAN bus overload detected",
                        severity="FATAL"
                    )
                    # Crash on FATAL alarm
                    import sys
                    logger.critical("FATAL alarm - stopping CANBusAdapter")
                    sys.exit(1)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"CAN bus polling error: {e}", exc_info=True)
                await asyncio.sleep(5)

    @classmethod
    async def get_latest_sensor_data(cls) -> List[SensorDataResponse]:
        return [SensorDataResponse(**d.dict()) for d in cls._latest_data[-10:]]
