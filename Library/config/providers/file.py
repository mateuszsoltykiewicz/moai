import os
import json
import aiofiles
import asyncio
from pathlib import Path
from watchfiles import awatch
from ..provider import ConfigProvider
from Library.logging import get_logger

logger = get_logger(__name__)

class FileConfigProvider(ConfigProvider):
    def __init__(self, config_path: str, env_prefix: str = "APP", reload_interval: float = 2.0):
        self.config_path = Path(config_path)
        self.env_prefix = env_prefix
        self.reload_interval = reload_interval

    async def setup(self):
        logger.info(f"Using file config: {self.config_path}")

    async def teardown(self):
        logger.info("Stopped file config watcher")

    async def load(self) -> dict:
        try:
            async with aiofiles.open(self.config_path, "r") as f:
                content = await f.read()
            config_data = json.loads(content)
            self._apply_env_overrides(config_data)
            logger.debug(f"Loaded config from file: {self.config_path}")
            return config_data
        except Exception as e:
            logger.error(f"Failed to load config file: {e}", exc_info=True)
            raise

    async def watch(self):
        try:
            async for _ in awatch(self.config_path):
                logger.info(f"Config file changed: {self.config_path}")
                yield
                await asyncio.sleep(self.reload_interval)
        except Exception as e:
            logger.error(f"File watch failed: {e}", exc_info=True)
            raise

    def _apply_env_overrides(self, config_: dict) -> None:
        # Implementation remains the same
        ...
