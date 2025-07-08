# /Python/libraries/core/config_hot_reload/__init__.py
import asyncio
import yaml

class AsyncConfigHotReloader:
    def __init__(self, config_path, reload_interval=10):
        self.config_path = config_path
        self.reload_interval = reload_interval
        self.config = self._load()

    def _load(self):
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    async def watch(self):
        while True:
            await asyncio.sleep(self.reload_interval)
            self.config = self._load()
