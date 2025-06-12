import asyncio
from typing import Any, Dict, Optional
from pathlib import Path
from pydantic import BaseModel, Field, validator
import json
from datetime import datetime
from AppLib.utils.logger import get_logger
from AppLib.core.config import AppConfig
import aiofiles
from cryptography.fernet import Fernet, InvalidToken

logger = get_logger(__name__)

class AppStateModel(BaseModel):
    """Versioned application state model"""
    version: int = Field(default=1, description="Schema version for migrations")
    service_ready: bool = Field(default=False)
    last_backup: Optional[datetime] = None
    connections: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    hardware_status: Dict[str, str] = Field(default_factory=dict)
    custom_state: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('version')
    def validate_version(cls, v):
        if v != 1:
            raise ValueError(f"Unsupported state version: {v}")
        return v

class AppState:
    """Production-grade state manager with encryption and versioning"""
    _instance: Optional['AppState'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state = AppStateModel()
            cls._instance._persistence_path = Path("state_backups/latest_state.json")
            cls._instance._backup_task: Optional[asyncio.Task] = None
            cls._instance._fernet: Optional[Fernet] = None
        return cls._instance

    async def initialize(self, config: AppConfig):
        """Initialize state with optional persistence restore"""
        async with self._lock:
            if config.persistence.enabled:
                restored = await self._restore_state()
                if not restored:
                    logger.warning("No valid state backup found, starting fresh.")
            self._state.service_ready = False
            logger.info("Application state initialized")

    async def get_state(self) -> AppStateModel:
        """Get a safe copy of current state"""
        async with self._lock:
            return self._state.copy()

    async def update_state(self, update: Dict[str, Any], persist: bool = False):
        """Partial state update with optional persistence"""
        async with self._lock:
            self._state = self._state.copy(update=update)
            
            if persist:
                await self._persist_state()
                
            logger.debug("State updated: %s", update)

    async def _persist_state(self):
        """Persist state with encryption if configured"""
        try:
            self._persistence_path.parent.mkdir(exist_ok=True)
            data = self._state.json().encode()
            
            if self._fernet:
                data = self._fernet.encrypt(data)
                mode = 'wb'
            else:
                mode = 'w'

            async with aiofiles.open(self._persistence_path, mode) as f:
                await f.write(data if mode == 'wb' else data.decode())
                
            self._state = self._state.copy(update={"last_backup": datetime.now()})
        except Exception as e:
            logger.error("State persistence failed: %s", str(e))

    async def _restore_state(self) -> bool:
        """Restore state with version handling and decryption"""
        try:
            if not self._persistence_path.exists():
                return False

            async with aiofiles.open(self._persistence_path, 'rb' if self._fernet else 'r') as f:
                data = await f.read()

            if self._fernet:
                try:
                    data = self._fernet.decrypt(data)
                except InvalidToken:
                    logger.error("State decryption failed: Invalid key or corrupted data.")
                    return False

            loaded = AppStateModel.parse_raw(data)
            
            # Version migration logic
            if loaded.version != AppStateModel().version:
                logger.warning("State version mismatch: backup=%s, current=%s",
                              loaded.version, AppStateModel().version)
                return False  # Implement migrations as needed

            self._state = loaded
            logger.info("State restored from backup")
            return True
        except Exception as e:
            logger.error("State restoration failed: %s", str(e))
            return False

    async def start_auto_backup(self, interval: int = 300):
        """Start periodic state backups"""
        async def backup_loop():
            while True:
                await asyncio.sleep(interval)
                await self._persist_state()
                
        self._backup_task = asyncio.create_task(backup_loop())
        logger.info("Automatic state backups enabled every %d seconds", interval)

    async def stop_auto_backup(self):
        """Stop automatic backups"""
        if self._backup_task:
            self._backup_task.cancel()
            logger.info("Automatic state backups stopped")

    def set_encryption_key(self, key: bytes):
        """Initialize encryption using Fernet symmetric key"""
        self._fernet = Fernet(key)
        logger.info("State encryption enabled")

    async def migrate_state(self, target_version: int):
        """Handle state schema migrations"""
        current_version = self._state.version
        
        while current_version < target_version:
            if current_version == 1:
                # Example migration from v1 to v2
                new_state = self._state.dict()
                new_state["version"] = 2
                new_state["new_field"] = "default"
                self._state = AppStateModel(**new_state)
                current_version = 2
                logger.info("Migrated state from v1 to v2")
                
            else:
                raise ValueError(f"No migration path from version {current_version}")
        
        await self._persist_state()

