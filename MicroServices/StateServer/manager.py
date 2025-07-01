import asyncio
import json
from typing import Dict, Any
from .schemas import StateUpdateRequest
from .metrics import record_state_operation
from Library.logging import get_logger
from Library.database.manager import DatabaseManager

logger = get_logger(__name__)

class StateServerManager:
    _lock = asyncio.Lock()
    _db = DatabaseManager()

    @classmethod
    async def setup(cls):
        await cls._db.setup()
        logger.info("StateServerManager setup complete.")

    @classmethod
    async def shutdown(cls):
        await cls._db.shutdown()
        logger.info("StateServerManager shutdown complete.")

    @classmethod
    async def get(cls, key: str) -> Any:
        async with cls._lock:
            record = await cls._db.get_record("state", key)
            if not record:
                raise Exception(f"State key {key} not found")
            record_state_operation("get")
            return record.get("value")

    @classmethod
    async def set(cls, key: str, value: Any):
        async with cls._lock:
            await cls._db.create_or_update("state", key, {"value": value})
            record_state_operation("set")
            logger.info(f"Set state for {key}")
