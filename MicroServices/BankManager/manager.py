import asyncio
from .schemas import TransactionRequest, TransactionResponse
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.events import KafkaProducer
from Library.alarms import AlarmClient
from Library.state import StateClient
from Library.config import ConfigManager

logger = get_logger(__name__)

class BankManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()
    _kafka_producer = KafkaProducer()
    _alarm_client = AlarmClient()
    _state_client = StateClient(service_name="BankManager")

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        await cls._kafka_producer.connect()
        await cls._state_client.setup()
        # Start Kafka consumer for sensorData
        asyncio.create_task(cls._consume_sensor_data())
        logger.info("BankManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._kafka_producer.disconnect()
        await cls._db.shutdown()
        logger.info("BankManager shutdown complete")

    @classmethod
    async def process_transaction(cls, req: TransactionRequest) -> TransactionResponse:
        async with cls._lock:
            # Business logic
            if req.amount > 10000:
                await cls._alarm_client.raise_alarm(
                    alarm_id="LARGE_TXN",
                    message=f"Large transaction: {req.amount}",
                    severity="WARNING"
                )
            
            # Save transaction
            await cls._db.create_record("transactions", req.dict())
            
            # Update state
            await cls._state_client.set(f"txn:{req.id}", req.dict())
            
            return TransactionResponse(
                id=req.id,
                status="SUCCESS",
                amount=req.amount
            )

    @classmethod
    async def _consume_sensor_data(cls):
        # Implementation for consuming sensorData
        # This would be a Kafka consumer listening to sensorData topic
        pass

    @classmethod
    async def _on_fatal_alarm(cls):
        logger.critical("FATAL alarm detected - crashing service")
        # Crash immediately on FATAL alarm
        import sys
        sys.exit(1)
