"""
StateManager: Centralized, async state management for the application.

- Manages application and component state
- Supports persistence and restoration
- Integrates with sessions for stateful resources
- Provides async lifecycle and listener registration
- Exposes metrics for state operations
"""

import asyncio
from typing import Dict, Any, Callable, Optional, Awaitable
from .schemas import StateResponse, StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError
from .metrics import record_state_operation
from .utils import log_info
from .central_state_adapter import CentralStateRegistryAdapter
from .kafka_adapter import KafkaStatePublisher

class StateManager:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._listeners: Dict[str, Callable[[str, Any], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._sessions = {}
        self._kafka_publisher = KafkaStatePublisher(kafka_manager) if kafka_manager else None


    async def get(self, key: str) -> Any:
        """
        Get value for a state key.
        """
        async with self._lock:
            if key not in self._state:
                raise StateNotFoundError(f"State key {key} not found")
            record_state_operation("get")
            log_info(f"StateManager: Retrieved state for key {key}")
            return self._state[key]

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._sessions[key] = value
            # Push to Central State Registry if enabled
            if self._csr_adapter:
                await self._csr_adapter.push_state(
                    service_name="my_service",
                    state={"key": key, "value": value}
                )

    async def update(self, key: str, updates: Dict[str, Any]) -> None:
        """
        Update value for a state key with a partial update.
        """
        async with self._lock:
            if key not in self._state:
                raise StateNotFoundError(f"State key {key} not found")
            current = self._state[key]
            if not isinstance(current, dict):
                raise StateValidationError(f"State value for {key} is not a dictionary")
            current.update(updates)
            record_state_operation("update")
            log_info(f"StateManager: Partial update for key {key}")
            await self._notify_listeners(key, current)

    async def delete(self, key: str) -> None:
        """
        Delete a state key.
        """
        async with self._lock:
            if key not in self._state:
                raise StateNotFoundError(f"State key {key} not found")
            del self._state[key]
            record_state_operation("delete")
            log_info(f"StateManager: Deleted state for key {key}")
            await self._notify_listeners(key, None)

    async def get_all(self) -> Dict[str, Any]:
        """
        Get all state.
        """
        async with self._lock:
            record_state_operation("get_all")
            log_info("StateManager: Retrieved all state")
            return dict(self._state)

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
