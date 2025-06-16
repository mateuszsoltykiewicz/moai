"""
Async, schema-driven configuration manager.

- Loads config from JSON file
- Applies environment variable overrides
- Validates with Pydantic schemas
- Supports hot reload and async listeners
"""

import os
import json
import asyncio
from typing import Any, Dict, Callable, Optional, Type, Awaitable
from pathlib import Path
import aiofiles
from watchfiles import awatch
from pydantic import BaseModel, ValidationError
from models.config import AppConfig  # Import your schema

class AsyncConfigManager:
    def __init__(
        self,
        config_path: str,
        schema: Type[BaseModel] = AppConfig,
        env_prefix: str = "APP",
        reload_interval: float = 2.0,
    ):
        self.config_path = Path(config_path)
        self.schema = schema
        self.env_prefix = env_prefix
        self.reload_interval = reload_interval
        self._current_config: Optional[BaseModel] = None
        self._listeners: Dict[str, Callable[[BaseModel], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._watch_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start config watcher and initial load."""
        await self._load()
        self._watch_task = asyncio.create_task(self._watch_config())

    async def stop(self) -> None:
        """Stop config watcher."""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass

    async def get(self) -> BaseModel:
        """Get current config (thread-safe)."""
        async with self._lock:
            if self._current_config is None:
                await self._load()
            return self._current_config

    def add_listener(self, name: str, callback: Callable[[BaseModel], Awaitable[None]]) -> None:
        """Register async listener for config changes."""
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """Remove config change listener."""
        self._listeners.pop(name, None)

    async def _load(self) -> None:
        async with self._lock:
            try:
                async with aiofiles.open(self.config_path, "r") as f:
                    content = await f.read()
                config_data = json.loads(content)
                self._apply_env_overrides(config_data)
                # Validate with Pydantic schema
                new_config = AppConfig.model_validate(config_data)
                self._current_config = new_config
                await self._notify_listeners()
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Config validation failed: {e}")
            except FileNotFoundError:
                print(f"Config file not found: {self.config_path}")

    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> None:
        """Apply environment variable overrides to config dict."""
        def set_nested(d: dict, keys: list, value: str):
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value

        for env_var, value in os.environ.items():
            if env_var.startswith(f"{self.env_prefix}__"):
                keys = env_var[len(self.env_prefix) + 2 :].lower().split("__")
                set_nested(config_data, keys, value)

    async def _watch_config(self) -> None:
        """Watch for config file changes and reload."""
        async for _ in awatch(self.config_path):
            await self._load()
            await asyncio.sleep(self.reload_interval)

    async def _notify_listeners(self) -> None:
        """Notify all async listeners of config changes."""
        if self._current_config:
            for callback in self._listeners.values():
                try:
                    await callback(self._current_config)
                except Exception as e:
                    print(f"Config listener error: {e}")

# Example usage:
# config_mgr = AsyncConfigManager("configs/dev/app_config.json")
# await config_mgr.start()
# config = await config_mgr.get()
# print(config.kafka.bootstrap_servers)
