import asyncio
from typing import Any, Dict, Callable, Awaitable, Optional, Type
from .schemas import AppConfig
from .exceptions import ConfigValidationError
from .metrics import record_config_operation, record_config_error
from Library.logging import get_logger

logger = get_logger(__name__)

class ConfigManager:
    def __init__(
        self,
        provider: 'ConfigProvider',
        schema: Type[AppConfig] = AppConfig,
        secrets_manager: Optional[Any] = None
    ):
        self.provider = provider
        self.schema = schema
        self.secrets_manager = secrets_manager
        self._current_config: Optional[AppConfig] = None
        self._listeners: Dict[str, Callable[[AppConfig], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._watch_task: Optional[asyncio.Task] = None
        self._fallback_config: Optional[dict] = None

    async def start(self) -> None:
        try:
            await self.provider.setup()
            await self._load()
            self._watch_task = asyncio.create_task(self._watch_changes())
            logger.info("ConfigManager started successfully")
        except Exception as e:
            logger.error(f"Config startup failed: {e}", exc_info=True)
            if self._fallback_config:
                self._current_config = self.schema.model_validate(self._fallback_config)
                logger.info("Using fallback configuration")

    async def stop(self) -> None:
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
        await self.provider.teardown()
        logger.info("ConfigManager stopped")

    async def get(self) -> AppConfig:
        async with self._lock:
            if self._current_config is None:
                await self._load()
            return self._current_config

    async def set(self, new_config: AppConfig) -> None:
        async with self._lock:
            self._current_config = new_config
            await self._notify_listeners()

    def add_listener(self, name: str, callback: Callable[[AppConfig], Awaitable[None]]) -> None:
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        self._listeners.pop(name, None)

    async def _load(self) -> None:
        async with self._lock:
            try:
                raw_config = await self.provider.load()
                if self.secrets_manager:
                    raw_config = await self._inject_secrets(raw_config)
                new_config = self.schema.model_validate(raw_config)
                self._current_config = new_config
                self._fallback_config = raw_config
                await self._notify_listeners()
                record_config_operation("load")
                logger.info("Config loaded and validated")
            except Exception as e:
                record_config_error()
                logger.error(f"Config validation failed: {e}", exc_info=True)
                raise ConfigValidationError(f"Config validation failed: {e}") from e

    async def _inject_secrets(self, config: dict) -> dict:
        # Implement secret injection logic if needed
        return config

    async def _watch_changes(self) -> None:
        while True:
            try:
                async for _ in self.provider.watch():
                    await self._load()
            except Exception as e:
                logger.error(f"Config watch failed: {e}. Reconnecting in 5s...", exc_info=True)
                await asyncio.sleep(5)
                await self.provider.setup()

    async def _notify_listeners(self) -> None:
        if self._current_config:
            for callback in self._listeners.values():
                try:
                    await callback(self._current_config)
                except Exception as e:
                    logger.error(f"Config listener error: {e}", exc_info=True)
