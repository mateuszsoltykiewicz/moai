import asyncio
import time
from typing import Optional
from .schemas import HeatingJobTriggerRequest, HeatingJobStatusResponse
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.events import KafkaProducer, KafkaConsumer
from Library.alarms import AlarmClient
from Library.state import StateClient
from Library.config import ConfigManager

logger = get_logger(__name__)

class HeatingJobManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()
    _kafka_producer = KafkaProducer(topic="I2CHeating")
    _sensor_consumer = KafkaConsumer(topic="sensorData")
    _alarm_client = AlarmClient()
    _state_client = StateClient(service_name="HeatingJob")
    _job_running: bool = False
    _last_temp: Optional[float] = None
    _job_start_time: Optional[float] = None

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        await cls._kafka_producer.connect()
        await cls._state_client.setup()
        await cls.clear_heating_alarms_on_startup()
        asyncio.create_task(cls._consume_sensor_data())
        logger.info("HeatingJobManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._kafka_producer.disconnect()
        await cls._db.shutdown()
        logger.info("HeatingJobManager shutdown complete")

    @classmethod
    async def clear_heating_alarms_on_startup(cls):
        await cls._alarm_client.clear_alarms(source="HeatingJob")
        logger.info("Cleared heating job-specific alarms on startup")

    @classmethod
    async def trigger_job(cls, req: HeatingJobTriggerRequest) -> HeatingJobStatusResponse:
        async with cls._lock:
            if cls._job_running:
                raise Exception("Heating job already running")
            cls._job_running = True
            cls._job_start_time = time.time()
            cls._last_temp = None
            await cls._alarm_client.raise_alarm(
                alarm_id="HEATING_JOB_STARTED",
                message="Heating job triggered",
                severity="INFO"
            )
            await cls._kafka_producer.produce({"action": "start", "timestamp": time.time()})
            await cls._state_client.set("HeatingJob:status", "running")
            asyncio.create_task(cls._monitor_temperature_change())
            logger.info("Heating job triggered")
            return HeatingJobStatusResponse(running=True, last_temp=None)

    @classmethod
    async def get_status(cls) -> HeatingJobStatusResponse:
        running = cls._job_running
        last_temp = cls._last_temp
        return HeatingJobStatusResponse(running=running, last_temp=last_temp)

    @classmethod
    async def _consume_sensor_data(cls):
        async for message in cls._sensor_consumer.listen():
            try:
                data = message["value"]
                if data.get("sensor") == "water_temp":
                    cls._last_temp = data.get("value")
                    if cls._job_running:
                        await cls._state_client.set("HeatingJob:last_temp", cls._last_temp)
            except Exception as e:
                logger.error(f"Sensor data processing error: {e}", exc_info=True)

    @classmethod
    async def _monitor_temperature_change(cls):
        """Fails with exit code 1 and raises alarm if temp doesn't change in time."""
        timeout = 60  # seconds, configurable
        initial_temp = cls._last_temp
        start_time = cls._job_start_time or time.time()
        while cls._job_running and (time.time() - start_time) < timeout:
            await asyncio.sleep(5)
            if cls._last_temp is not None and cls._last_temp != initial_temp:
                await cls._alarm_client.delete_alarm("HEATING_JOB_STARTED")
                await cls._alarm_client.raise_alarm(
                    alarm_id="HEATING_JOB_FINISHED",
                    message="Heating job finished successfully",
                    severity="INFO"
                )
                await cls._state_client.set("HeatingJob:status", "finished")
                cls._job_running = False
                logger.info("Heating job finished successfully")
                return
        # Timeout: fail job
        await cls._alarm_client.raise_alarm(
            alarm_id="HEATING_JOB_FAILED",
            message="No temperature change detected in time",
            severity="FATAL"
        )
        await cls._state_client.set("HeatingJob:status", "failed")
        logger.critical("Heating job failed - exiting with code 1")
        import sys
        sys.exit(1)
