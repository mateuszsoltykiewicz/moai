import asyncio
from datetime import datetime
from typing import List, Optional
from Library.database.manager import DatabaseManager
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError
from .metrics import record_central_alarm_operation
from .utils import log_info

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
            log_info(f"CentralAlarmsRegistry: Raised alarm {alarm.id} ({alarm.type}) from {alarm.source}")
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
            log_info(f"CentralAlarmsRegistry: Cleared alarm {alarm.id}")
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
