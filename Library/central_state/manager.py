import asyncio
from typing import Dict
from .schemas import ServiceState
from datetime import datetime, timedelta

class CentralStateRegistry:
    def __init__(self, heartbeat_timeout: int = 30):
        self._services: Dict[str, ServiceState] = {}
        self._lock = asyncio.Lock()
        self.heartbeat_timeout = heartbeat_timeout

    async def register_or_update(self, state: ServiceState):
        async with self._lock:
            self._services[state.name] = state

    async def get_service(self, name: str) -> ServiceState:
        async with self._lock:
            return self._services.get(name)

    async def list_services(self) -> Dict[str, ServiceState]:
        async with self._lock:
            # Optionally, mark stale services as "unhealthy"
            now = datetime.timezone.utc()
            for svc in self._services.values():
                if (now - svc.last_heartbeat).total_seconds() > self.heartbeat_timeout:
                    svc.status = "stale"
            return dict(self._services)
