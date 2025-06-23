import asyncio
from typing import Dict, List
from datetime import datetime
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError
from .metrics import record_central_alarm_operation

class CentralAlarmsRegistry:
    """
    Central registry for all alarms across microservices.
    """
    def __init__(self):
        self._alarms: Dict[str, CentralAlarm] = {}
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
            self._alarms[alarm.id] = alarm
            record_central_alarm_operation("raise")
            return alarm

    async def clear_alarm(self, req: AlarmClearRequest) -> CentralAlarm:
        async with self._lock:
            alarm = self._alarms.get(req.id)
            if not alarm:
                raise CentralAlarmNotFoundError(f"Alarm {req.id} not found")
            alarm.active = False
            alarm.cleared_at = req.cleared_at or datetime.utcnow()
            record_central_alarm_operation("clear")
            return alarm

    async def get_alarm(self, alarm_id: str) -> CentralAlarm:
        async with self._lock:
            alarm = self._alarms.get(alarm_id)
            if not alarm:
                raise CentralAlarmNotFoundError(f"Alarm {alarm_id} not found")
            return alarm

    async def list_alarms(self, active_only: bool = False) -> List[CentralAlarm]:
        async with self._lock:
            alarms = list(self._alarms.values())
            if active_only:
                alarms = [a for a in alarms if a.active]
            return alarms
