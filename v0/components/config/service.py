"""
Async ConfigService for hot-reload and dynamic updates.
- Watches config files for changes.
- Validates new configs.
- Notifies listeners on successful reload.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Any
from AppLib.utils.config_validator import validate_config_file, ConfigValidationError
from AppLib.core.config import AppConfig
from AppLib.utils.logger import get_logger

logger = get_logger(__name__)

class ConfigService:
    """
    Async config service supporting hot reload and dynamic updates.
    """
    def __init__(
        self,
        config_path: str,
        schema_path: str,
        reload_interval: int = 5
    ):
        self.config_path = config_path
        self.schema_path = schema_path
        self.reload_interval = reload_interval
        self._listeners: List[Callable[[AppConfig], Any]] = []
        self._current_config: Optional[AppConfig] = None
        self._last_mtime: Optional[float] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def register_listener(self, callback: Callable[[AppConfig], Any]):
        """
        Register a callback to be called on config reload.
        """
        self._listeners.append(callback)

    async def start(self):
        """
        Start the background config watcher.
        """
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info("ConfigService started with hot-reload.")

    async def stop(self):
        """
        Stop the background watcher.
        """
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("ConfigService stopped.")

    async def _watch_loop(self):
        """
        Watch config file for changes and reload if needed.
        """
        while self._running:
            try:
                mtime = os.path.getmtime(self.config_path)
                if self._last_mtime is None or mtime != self._last_mtime:
                    await self.reload()
                    self._last_mtime = mtime
            except Exception as e:
                logger.error(f"ConfigService watch loop error: {e}")
            await asyncio.sleep(self.reload_interval)

    async def reload(self):
        """
        Reload and validate config. Notify listeners if successful.
        """
        try:
            validate_config_file(self.config_path, self.schema_path, config_name="AppConfig")
            with open(self.config_path, "r") as f:
                config_data = json.load(f)
            new_config = AppConfig(**config_data)
            self._current_config = new_config
            logger.info("Config reloaded and validated.")
            for listener in self._listeners:
                # Callbacks can be async or sync
                if asyncio.iscoroutinefunction(listener):
                    await listener(new_config)
                else:
                    listener(new_config)
        except (ConfigValidationError, Exception) as e:
            logger.error(f"Config reload failed: {e}")

    def get(self) -> Optional[AppConfig]:
        """
        Get the current loaded config.
        """
        return self._current_config

"""
from AppLib.services.config.service import ConfigService

config_service = ConfigService(
    config_path="configs/dev/app_config.json",
    schema_path="schemas/validation/app_config.schema.json"
)

# Example: Register a listener to react to config changes
def on_config_update(new_config):
    print("Config updated!", new_config)

config_service.register_listener(on_config_update)

# In your FastAPI lifespan or startup
await config_service.start()

# On shutdown
await config_service.stop()

"""