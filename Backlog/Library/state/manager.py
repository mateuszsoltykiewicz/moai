import asyncio
import json
from typing import Dict, Any, Callable, Optional, Awaitable
from .schemas import StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError
from .metrics import record_state_operation, record_state_error
from Library.logging import get_logger
from Library.database.manager import DatabaseManager
from Library.events.bus import EventBus
from redis.asyncio import Redis

logger = get_logger(__name__)

class StateManager:
    def __init__(
        self,
        db_manager: DatabaseManager,
        event_bus: Optional[EventBus] = None,
        redis: Optional[Redis] = None,
        service_name: str = "default"
    ):
        self._db = db_manager
        self._event_bus = event_bus
        self._redis = redis
        self._service_name = service_name
        self._listeners: Dict[str, Callable[[str, Any], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._distributed_lock = redis.lock if redis else None

    async def get(self, key: str) -> Any:
        async with self._lock:
            try:
                # Redis cache check
                if self._redis:
                    cached = await self._redis.get(f"state:{key}")
                    if cached:
                        return json.loads(cached)
                
                # Database retrieval
                record = await self._db.get_record("state", key)
                if not record:
                    raise StateNotFoundError(f"State key {key} not found")
                
                value = record.get("value")
                
                # Update cache
                if self._redis:
                    await self._redis.set(
                        f"state:{key}", 
                        json.dumps(value),
                        ex=300  # 5min TTL
                    )
                
                record_state_operation("get")
                return value
            except Exception as e:
                record_state_error("get", "error")
                logger.error(f"State get failed for {key}: {e}", exc_info=True)
                raise

    async def set(self, key: str, value: Any):
        lock = self._distributed_lock(f"state_lock:{key}") if self._distributed_lock else self._lock
        
        async with lock:
            try:
                # State size validation
                state_json = json.dumps(value)
                if len(state_json) > 1024 * 1024:
                    raise StateValidationError("State value exceeds 1MB limit")
                
                # Database operation
                await self._db.create_or_update("state", key, {"value": value})
                
                # Update cache
                if self._redis:
                    await self._redis.set(f"state:{key}", state_json, ex=300)
                
                # Notify listeners
                await self._notify_listeners(key, value)
                
                # Publish state change
                if self._event_bus:
                    await self._event_bus.publish(
                        "StateUpdated",
                        {
                            "service": self._service_name,
                            "key": key,
                            "value": value
                        }
                    )
                
                record_state_operation("set")
            except Exception as e:
                record_state_error("set", "error")
                logger.error(f"State set failed for {key}: {e}", exc_info=True)
                raise

    async def update(self, key: str, updates: Dict[str, Any]) -> None:
        async with self._lock:
            try:
                current = await self.get(key)
                if not isinstance(current, dict):
                    raise StateValidationError(f"State value for {key} is not a dictionary")
                
                new_value = {**current, **updates}
                await self.set(key, new_value)
                record_state_operation("update")
            except Exception as e:
                record_state_error("update", "error")
                logger.error(f"State update failed for {key}: {e}", exc_info=True)
                raise

    async def delete(self, key: str) -> None:
        async with self._lock:
            try:
                await self._db.delete_record("state", key)
                if self._redis:
                    await self._redis.delete(f"state:{key}")
                await self._notify_listeners(key, None)
                record_state_operation("delete")
            except Exception as e:
                record_state_error("delete", "error")
                logger.error(f"State delete failed for {key}: {e}", exc_info=True)
                raise

    async def get_all(self) -> Dict[str, Any]:
        try:
            records = await self._db.query_records("state", limit=1000)
            return {rec["id"]: rec["value"] for rec in records}
        except Exception as e:
            record_state_error("get_all", "error")
            logger.error(f"State get_all failed: {e}", exc_info=True)
            raise

    def add_listener(self, name: str, callback: Callable[[str, Any], Awaitable[None]]) -> None:
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        self._listeners.pop(name, None)

    async def _notify_listeners(self, key: str, value: Any) -> None:
        for callback in self._listeners.values():
            try:
                await callback(key, value)
            except Exception as e:
                logger.error(f"State listener error: {e}", exc_info=True)
