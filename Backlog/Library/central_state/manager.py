import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from Library.database.manager import DatabaseManager
from .schemas import ServiceState
from .metrics import record_state_operation, update_service_count
from Library.logging import get_logger

logger = get_logger(__name__)

class CentralStateRegistry:
    """
    Central service registry with health monitoring and persistence.
    """
    def __init__(self, db_manager: DatabaseManager, heartbeat_timeout: int = 30):
        self._db_manager = db_manager
        self._lock = asyncio.Lock()
        self.heartbeat_timeout = heartbeat_timeout

    async def register_or_update(self, state: ServiceState) -> ServiceState:
        async with self._lock:
            await self._db_manager.create_or_update(
                "services", 
                state.name, 
                state.dict()
            )
            record_state_operation("register")
            logger.info(f"Registered/updated service: {state.name}")
            await self._update_service_count()
            return state

    async def get_service(self, name: str) -> Optional[ServiceState]:
        async with self._lock:
            service_data = await self._db_manager.get_record("services", name)
            if not service_data:
                return None
            return ServiceState(**service_data)

    async def list_services(self) -> List[ServiceState]:
        async with self._lock:
            services_data = await self._db_manager.query_records("services")
            now = datetime.now(timezone.utc)
            updated_services = []
            
            for data in services_data:
                service = ServiceState(**data)
                if (now - service.last_heartbeat).total_seconds() > self.heartbeat_timeout:
                    service.status = "stale"
                    await self._db_manager.update_record("services", service.name, service.dict())
                updated_services.append(service)
            
            await self._update_service_count()
            return updated_services

    async def _update_service_count(self):
        """Update service count metric"""
        try:
            services = await self._db_manager.query_records("services")
            update_service_count(len(services))
        except Exception as e:
            logger.error(f"Failed to update service count: {e}", exc_info=True)
