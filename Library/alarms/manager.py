"""
AlarmsManager: Centralized alarm and event management.

- Stores, raises, clears, and queries alarms
- Notifies listeners on alarm changes
- Integrates with metrics, logging, and other managers
- Async and thread-safe
"""

import asyncio
from typing import Dict, Any, Callable, Awaitable, List, Optional
from .schemas import Alarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import AlarmNotFoundError
from .metrics import record_alarm_operation
from .utils import log_info
from .central_registry_adapter import CentralAlarmsAdapter

class AlarmsManager:
    def __init__(self, central_registry_url: Optional[str] = None):
        self._alarms: Dict[str, Alarm] = {}
        self._listeners: Dict[str, Callable[[Alarm], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self.central_adapter = CentralAlarmsAdapter(central_registry_url) if central_registry_url else None

    async def raise_alarm(self, alarm_req: AlarmRaiseRequest) -> Alarm:
        """
        Raise or update an alarm.
        """
        async with self._lock:
            alarm = Alarm(
                id=alarm_req.id,
                source=alarm_req.source,
                type=alarm_req.type,
                details=alarm_req.details,
                active=True
            )
            if self.central_adapter:
                await self.central_adapter.raise_alarm(alarm_req)
            self._alarms[alarm.id] = alarm
            record_alarm_operation("raise")
            log_info(f"AlarmsManager: Raised alarm {alarm.id} ({alarm.type}) from {alarm.source}")
            await self._notify_listeners(alarm)
            return alarm

    async def clear_alarm(self, alarm_req: AlarmClearRequest) -> Alarm:
        """
        Clear (deactivate) an alarm.
        """
        async with self._lock:
            alarm = self._alarms.get(alarm_req.id)
            if not alarm:
                raise AlarmNotFoundError(f"Alarm {alarm_req.id} not found")
            alarm.active = False
            record_alarm_operation("clear")
            log_info(f"AlarmsManager: Cleared alarm {alarm.id}")
            await self._notify_listeners(alarm)
            return alarm

    async def get_alarm(self, alarm_id: str) -> Alarm:
        """
        Get alarm by ID.
        """
        async with self._lock:
            alarm = self._alarms.get(alarm_id)
            if not alarm:
                raise AlarmNotFoundError(f"Alarm {alarm_id} not found")
            return alarm

    async def list_alarms(self, active_only: bool = False) -> List[Alarm]:
        """
        List all alarms, optionally filtering by active status.
        """
        async with self._lock:
            alarms = list(self._alarms.values())
            if active_only:
                alarms = [a for a in alarms if a.active]
            return alarms

    def add_listener(self, name: str, callback: Callable[[Alarm], Awaitable[None]]) -> None:
        """
        Register async listener for alarm changes.
        """
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """
        Remove alarm change listener.
        """
        self._listeners.pop(name, None)

    async def _notify_listeners(self, alarm: Alarm) -> None:
        """
        Notify all listeners of an alarm change.
        """
        for callback in self._listeners.values():
            try:
                await callback(alarm)
            except Exception as e:
                log_info(f"Alarm listener error: {e}")
