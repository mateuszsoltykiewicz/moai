# config/manager.py

import asyncio
from typing import Any, Dict, Callable, Awaitable, Optional, Type
from .schemas import AppConfig
from .exceptions import ConfigValidationError
from .metrics import record_config_operation
from .utils import log_info

class ConfigManager:
    def __init__(
        self,
        provider: str = 'ConfigProvider',
        schema: Type[AppConfig] = AppConfig,
    ):
        self.provider = provider
        self.schema = schema
        self._current_config: Optional[AppConfig] = None
        self._listeners: Dict[str, Callable[[AppConfig], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._watch_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start config provider and initial load."""
        await self.provider.setup()
        await self._load()
        self._watch_task = asyncio.create_task(self._watch_changes())

    async def stop(self) -> None:
        """Stop config watcher."""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
        await self.provider.teardown()

    async def get(self) -> AppConfig:
        """Get current config (thread-safe)."""
        async with self._lock:
            if self._current_config is None:
                await self._load()
            return self._current_config

    def add_listener(self, name: str, callback: Callable[[AppConfig], Awaitable[None]]) -> None:
        """Register async listener for config changes."""
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """Remove config change listener."""
        self._listeners.pop(name, None)

    async def _load(self) -> None:
        """Load and validate configuration."""
        async with self._lock:
            try:
                raw_config = await self.provider.load()
                new_config = self.schema.model_validate(raw_config)
                self._current_config = new_config
                await self._notify_listeners()
                record_config_operation("load")
                log_info("ConfigManager: Config loaded and validated.")
            except Exception as e:
                raise ConfigValidationError(f"Config validation failed: {e}")

    async def _watch_changes(self) -> None:
        """Watch for configuration changes."""
        async for _ in self.provider.watch():
            await self._load()

    async def _notify_listeners(self) -> None:
        """Notify all async listeners of config changes."""
        if self._current_config:
            for callback in self._listeners.values():
                try:
                    await callback(self._current_config)
                except Exception as e:
                    log_info(f"Config listener error: {e}")
