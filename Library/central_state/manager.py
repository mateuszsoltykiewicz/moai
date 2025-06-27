import asyncio
from datetime import datetime, timezone
from typing import Dict, List
from Library.database.manager import DatabaseManager
from .schemas import ServiceState
from .metrics import record_state_operation
from .utils import log_info

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
            # Create or update service state in database
            await self._db_manager.create_or_update(
                "services", 
                state.name, 
                state.dict()
            )
            record_state_operation("register")
            log_info(f"Registered/updated service: {state.name}")
            return state

    async def get_service(self, name: str) -> Optional[ServiceState]:
        async with self._lock:
            service_data = await self._db_manager.get_record("services", name)
            if not service_data:
                return None
            return ServiceState(**service_data)

    async def list_services(self) -> List[ServiceState]:
        async with self._lock:
            # Get all services from database
            services_data = await self._db_manager.query_records("services")
            
            # Check health status
            now = datetime.now(timezone.utc)
            updated_services = []
            
            for data in services_data:
                service = ServiceState(**data)
                # Update status if heartbeat is stale
                if (now - service.last_heartbeat).total_seconds() > self.heartbeat_timeout:
                    service.status = "stale"
                    await self._db_manager.update_record("services", service.name, service.dict())
                updated_services.append(service)
            
            return updated_services
