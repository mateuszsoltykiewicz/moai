import asyncio
from typing import List, Optional, Dict
from .schemas import ExceptionPayload
from .exceptions import ExceptionNotFoundError
from .metrics import record_exceptions_operation
from Library.logging import get_logger

logger = get_logger(__name__)

class CentralExceptionsManager:
    def __init__(self, db_manager, alerting_manager=None):
        self._db_manager = db_manager
        self._alerting_manager = alerting_manager
        self._lock = asyncio.Lock()

    async def process_exception(self, payload: ExceptionPayload):
        async with self._lock:
            await self._db_manager.create_record("exceptions", payload.dict())
            record_exceptions_operation("process")
            logger.info(f"Exception processed: {payload.type} from {payload.service_name}")

            # Optional alerting
            if self._alerting_manager:
                await self._alerting_manager.send_alert(
                    title=f"Exception: {payload.type}",
                    message=payload.message,
                    details=payload.dict()
                )

    async def query_exceptions(self, exception_type: Optional[str] = None, service_name: Optional[str] = None, limit: int = 100) -> List[ExceptionPayload]:
        async with self._lock:
            filters = {}
            if exception_type:
                filters["type"] = exception_type
            if service_name:
                filters["service_name"] = service_name
            records = await self._db_manager.query_records("exceptions", filters=filters, limit=limit)
            return [ExceptionPayload(**rec) for rec in records]

    async def get_stats(self) -> Dict[str, int]:
        async with self._lock:
            records = await self._db_manager.query_records("exceptions")
            stats = {}
            for rec in records:
                etype = rec.get("type", "unknown")
                stats[etype] = stats.get(etype, 0) + 1
            return stats
