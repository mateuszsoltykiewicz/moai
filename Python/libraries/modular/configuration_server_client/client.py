import asyncio
import httpx
import jsonschema
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class ConfigurationServerClient:
    def __init__(self, base_url, service_name, token, schema, logger=None):
        self.base_url = base_url
        self.service_name = service_name
        self.token = token
        self.schema = schema
        self.logger = logger or setup_async_logger("config_client")
        self.config = None
        self.version = None

    @async_retry(max_attempts=5, delay=2)
    async def fetch_config(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/config/{self.service_name}", headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            jsonschema.validate(instance=data["config"], schema=self.schema)
            self.config = data["config"]
            self.version = data["version"]
            self.logger.info(f"Fetched config version {self.version}")
            return self.config

    async def watch_for_changes(self, poll_interval=10):
        while True:
            try:
                config = await self.fetch_config()
                # Implement callback or reload logic as needed
            except Exception as e:
                self.logger.error(f"Failed to fetch config: {e}")
            await asyncio.sleep(poll_interval)
