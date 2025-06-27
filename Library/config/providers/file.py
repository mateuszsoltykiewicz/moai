import os
import json
import aiofiles
import asyncio
from pathlib import Path
from watchfiles import awatch
from ..provider import ConfigProvider

class FileConfigProvider(ConfigProvider):
    def __init__(self, config_path: str, env_prefix: str = "APP", reload_interval: float = 2.0):
        self.config_path = Path(config_path)
        self.env_prefix = env_prefix
        self.reload_interval = reload_interval

    async def setup(self):
        pass

    async def teardown(self):
        pass

    async def load(self) -> dict:
        async with aiofiles.open(self.config_path, "r") as f:
            content = await f.read()
        config_data = json.loads(content)
        self._apply_env_overrides(config_data)
        return config_data

    async def watch(self):
        async for _ in awatch(self.config_path):
            yield
            await asyncio.sleep(self.reload_interval)

    def _apply_env_overrides(self, config_: Dict[str, Any]) -> None:
        def set_nested(d: dict, keys: list, value: str):
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value

        for env_var, value in os.environ.items():
            if env_var.startswith(f"{self.env_prefix}__"):
                keys = env_var[len(self.env_prefix) + 2 :].lower().split("__")
                set_nested(config_, keys, value)
