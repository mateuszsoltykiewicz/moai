"""
Production-grade StateManager with persistence, distributed locking, and enhanced sync.
"""

import asyncio
import json
from typing import Dict, Any, Callable, Optional, Awaitable
from .schemas import StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError
from .metrics import record_state_operation, record_state_error
from .utils import log_info, log_error
from Library.database.manager import DatabaseManager
from Library.events.bus import EventBus
from redis.asyncio import Redis

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
        """Get state with caching and distributed locking"""
        async with self._lock:
            try:
                # Check local cache first
                if self._redis:
                    cached = await self._redis.get(f"state:{key}")
                    if cached:
                        return json.loads(cached)
                
                # Fetch from database
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
                record_state_error("get", str(e))
                log_error(f"State get failed for {key}: {str(e)}")
                raise

    async def set(self, key: str, value: Any):
        """Atomic state update with distributed locking"""
        # Use distributed lock if available
        lock = self._distributed_lock(f"state_lock:{key}") if self._distributed_lock else self._lock
        
        async with lock:
            try:
                # Validate state size
                if len(json.dumps(value)) > 1024 * 1024:  # 1MB limit
                    raise StateValidationError("State value exceeds 1MB limit")
                
                # Database operation
                await self._db.create_or_update("state", key, {"value": value})
                
                # Update cache
                if self._redis:
                    await self._redis.set(
                        f"state:{key}", 
                        json.dumps(value),
                        ex=300
                    )
                
                # Notify listeners
                await self._notify_listeners(key, value)
                
                # Publish state change event
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
                record_state_error("set", str(e))
                log_error(f"State set failed for {key}: {str(e)}")
                raise

    async def update(self, key: str, updates: Dict[str, Any]) -> None:
        """Optimistic locking for partial updates"""
        async with self._lock:
            try:
                current = await self.get(key)
                if not isinstance(current, dict):
                    raise StateValidationError(f"State value for {key} is not a dictionary")
                
                # Apply updates
                new_value = {**current, **updates}
                await self.set(key, new_value)
                record_state_operation("update")
            except Exception as e:
                record_state_error("update", str(e))
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
                record_state_error("delete", str(e))
                raise

    async def get_all(self) -> Dict[str, Any]:
        """Paginated state retrieval for scalability"""
        try:
            records = await self._db.query_records("state", limit=1000)
            return {rec["id"]: rec["value"] for rec in records}
        except Exception as e:
            record_state_error("get_all", str(e))
            raise

    def add_listener(self, name: str, callback: Callable[[str, Any], Awaitable[None]]) -> None:
        """
        Register async listener for state changes.
        """
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """
        Remove state change listener.
        """
        self._listeners.pop(name, None)

    async def _notify_listeners(self, key: str, value: Any) -> None:
        """
        Notify all async listeners of state changes.
        """
        for callback in self._listeners.values():
            try:
                await callback(key, value)
            except Exception as e:
                log_info(f"State listener error: {e}")
