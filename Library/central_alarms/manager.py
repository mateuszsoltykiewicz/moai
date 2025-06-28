import asyncio
from datetime import datetime
from typing import List, Optional
from Library.database.manager import DatabaseManager
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError
from .metrics import record_central_alarm_operation, update_active_alarms_count
from Library.logging import get_logger

logger = get_logger(__name__)

class CentralAlarmsRegistry:
    """
    Central registry for all alarms across microservices.
    """
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager
        self._lock = asyncio.Lock()

    async def raise_alarm(self, req: AlarmRaiseRequest) -> CentralAlarm:
        async with self._lock:
            alarm = CentralAlarm(
                id=req.id,
                source=req.source,
                type=req.type,
                details=req.details,
                active=True,
                raised_at=datetime.utcnow(),
                cleared_at=None
            )
            await self._db_manager.create_record("alarms", alarm.dict())
            record_central_alarm_operation("raise")
            logger.info(f"Raised alarm {alarm.id} ({alarm.type}) from {alarm.source}")
            await self._update_alarms_count()
            return alarm

    async def clear_alarm(self, req: AlarmClearRequest) -> CentralAlarm:
        async with self._lock:
            alarm_data = await self._db_manager.get_record("alarms", req.id)
            if not alarm_data:
                raise CentralAlarmNotFoundError(f"Alarm {req.id} not found")
            alarm = CentralAlarm(**alarm_data)
            alarm.active = False
            alarm.cleared_at = req.cleared_at or datetime.utcnow()
            await self._db_manager.update_record("alarms", alarm.id, alarm.dict())
            record_central_alarm_operation("clear")
            logger.info(f"Cleared alarm {alarm.id}")
            await self._update_alarms_count()
            return alarm

    async def get_alarm(self, alarm_id: str) -> CentralAlarm:
        async with self._lock:
            alarm_data = await self._db_manager.get_record("alarms", alarm_id)
            if not alarm_data:
                raise CentralAlarmNotFoundError(f"Alarm {alarm_id} not found")
            return CentralAlarm(**alarm_data)

    async def list_alarms(self, active_only: bool = False) -> List[CentralAlarm]:
        async with self._lock:
            if active_only:
                alarms_data = await self._db_manager.query_records("alarms", {"active": True})
            else:
                alarms_data = await self._db_manager.query_records("alarms")
            return [CentralAlarm(**data) for data in alarms_data]

    async def _update_alarms_count(self):
        """Update active alarms gauge metric"""
        try:
            active_alarms = await self.list_alarms(active_only=True)
            update_active_alarms_count(len(active_alarms))
        except Exception as e:
            logger.error(f"Failed to update alarms count: {e}", exc_info=True)
