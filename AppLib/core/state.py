"""
Async Application State Manager with Encryption and Schema Versioning

Features:
- Thread-safe async operations
- Configurable encryption using Fernet
- Automatic schema migrations
- Periodic state backups
- Metrics and alarms integration
- Comprehensive logging
- File system persistence
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List, Awaitable

import aiofiles
from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class StateManagementError(Exception):
    """Base exception for state management errors."""
    pass

class AppStateModel(BaseModel):
    """
    Base model for application state with versioning support.
    
    Attributes:
        version: Schema version for migration handling
        service_ready: Service health status
        last_backup: Timestamp of last successful backup
        connections: Active service connections
        metrics: Collected system metrics
        hardware_status: Hardware component statuses
        custom_state: Custom application-specific state
    """
    version: int = Field(default=1, description="Schema version for migrations")
    service_ready: bool = Field(default=False, description="Service health status")
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    connections: Dict[str, Any] = Field(default_factory=dict, description="Active connections")
    metrics: Dict[str, float] = Field(default_factory=dict, description="System metrics")
    hardware_status: Dict[str, str] = Field(default_factory=dict, description="Hardware statuses")
    custom_state: Dict[str, Any] = Field(default_factory=dict, description="Custom state storage")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        validate_assignment = True

class AppState:
    """
    Thread-safe async state manager with encryption and persistence.
    
    Example:
        >>> state = AppState()
        >>> await state.initialize()
        >>> await state.update_state({"service_ready": True}, persist=True)
    """
    
    _instance: Optional['AppState'] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state = AppStateModel()
            cls._instance._listeners = []
            cls._instance._persistence_path = Path(os.getenv("STATE_PATH", "state_backups/latest_state.json"))
            cls._instance._backup_task = None
            cls._instance._fernet = None
            cls._instance._backup_interval = int(os.getenv("BACKUP_INTERVAL", "300"))
        return cls._instance

    async def initialize(self) -> None:
        """Initialize state manager and restore previous state if available."""
        async with self._lock:
            if await self._restore_state():
                logger.info("State restored from backup")
            else:
                logger.info("Initializing fresh state")
            await self.start_auto_backup()

    async def get_state(self) -> AppStateModel:
        """Retrieve a safe copy of the current state."""
        async with self._lock:
            return self._state.copy()

    async def update_state(self, update: Dict[str, Any], persist: bool = False) -> None:
        """
        Update application state with optional persistence.
        
        Args:
            update: Dictionary of state updates
            persist: Immediately persist changes to disk
            
        Raises:
            StateManagementError: On invalid state update
        """
        async with self._lock:
            try:
                self._state = self._state.copy(update=update)
                await self._notify_listeners()
                
                if persist:
                    await self._persist_state()
                    
                logger.debug("State updated: %s", update)
                # Record metric example
                # await metrics.record("state_updates", 1)
                
            except ValidationError as e:
                error_msg = f"Invalid state update: {str(e)}"
                # Raise alarm example
                # await alarms.raise("STATE_UPDATE_ERROR", error_msg)
                logger.error(error_msg)
                raise StateManagementError(error_msg) from e

    def add_listener(self, callback: Callable[[AppStateModel], Awaitable[None]]) -> None:
        """Register callback for state change notifications."""
        self._listeners.append(callback)

    async def start_auto_backup(self) -> None:
        """Enable periodic state backups."""
        if self._backup_task and not self._backup_task.done():
            return

        async def backup_loop():
            while True:
                await asyncio.sleep(self._backup_interval)
                await self._persist_state()
                logger.info("Periodic state backup completed")

        self._backup_task = asyncio.create_task(backup_loop())
        logger.info("Automatic backups enabled every %ds", self._backup_interval)

    async def stop_auto_backup(self) -> None:
        """Disable periodic state backups."""
        if self._backup_task:
            self._backup_task.cancel()
            logger.info("Automatic backups disabled")

    def configure_encryption(self, key: bytes) -> None:
        """
        Enable state encryption using Fernet symmetric encryption.
        
        Args:
            key: 32-byte URL-safe base64 encoded encryption key
            
        Raises:
            ValueError: For invalid key format
        """
        try:
            self._fernet = Fernet(key)
            logger.info("State encryption enabled")
        except ValueError as e:
            logger.error("Invalid encryption key: %s", str(e))
            raise

    async def migrate_state(self, target_version: int) -> None:
        """
        Execute schema migrations to reach target version.
        
        Args:
            target_version: Desired schema version
            
        Raises:
            StateManagementError: For unsupported migrations
        """
        async with self._lock:
            current_version = self._state.version
            while current_version < target_version:
                if current_version == 1:
                    # Example migration
                    new_state = self._state.dict()
                    new_state["version"] = 2
                    new_state["new_field"] = "default"
                    self._state = AppStateModel(**new_state)
                    current_version = 2
                    logger.info("Migrated state from v1 to v2")
                else:
                    error_msg = f"No migration path from v{current_version}"
                    logger.error(error_msg)
                    raise StateManagementError(error_msg)
            await self._persist_state()

    async def _persist_state(self) -> None:
        """Persist current state to disk with encryption."""
        try:
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            data = self._state.json().encode()
            
            if self._fernet:
                data = self._fernet.encrypt(data)

            async with aiofiles.open(self._persistence_path, "wb") as f:
                await f.write(data)
                
            self._state.last_backup = datetime.now()
            logger.debug("State persisted successfully")
            # Record metric example
            # await metrics.record("state_backups", 1)
            
        except (IOError, InvalidToken) as e:
            error_msg = f"State persistence failed: {str(e)}"
            # Raise alarm example
            # await alarms.raise("STATE_PERSIST_ERROR", error_msg)
            logger.error(error_msg)
            raise StateManagementError(error_msg) from e

    async def _restore_state(self) -> bool:
        """Restore state from disk with decryption and validation."""
        try:
            if not self._persistence_path.exists():
                return False

            async with aiofiles.open(self._persistence_path, "rb") as f:
                data = await f.read()

            if self._fernet:
                data = self._fernet.decrypt(data)

            loaded = AppStateModel.parse_raw(data)
            
            if loaded.version != self._state.version:
                await self.migrate_state(loaded.version)

            self._state = loaded
            return True
            
        except (ValidationError, InvalidToken, json.JSONDecodeError) as e:
            error_msg = f"State restoration failed: {str(e)}"
            # Raise alarm example
            # await alarms.raise("STATE_RESTORE_ERROR", error_msg)
            logger.error(error_msg)
            return False

    async def _notify_listeners(self) -> None:
        """Notify registered listeners of state changes."""
        for callback in self._listeners:
            try:
                await callback(self._state)
            except Exception as e:
                logger.error("Listener error: %s", str(e))
