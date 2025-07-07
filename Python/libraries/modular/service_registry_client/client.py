import httpx
import asyncio
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class ServiceRegistryClient:
    def __init__(self, base_url, token, service_name, logger=None):
        self.base_url = base_url
        self.token = token
        self.service_name = service_name
        self.logger = logger or setup_async_logger("service_registry_client")

    @async_retry(max_attempts=5, delay=2)
    async def register(self, metadata):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/register/{self.service_name}", json=metadata, headers=headers
            )
            resp.raise_for_status()
            self.logger.info(f"Registered service {self.service_name}")

    @async_retry(max_attempts=5, delay=2)
    async def heartbeat(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/heartbeat/{self.service_name}", headers=headers
            )
            resp.raise_for_status()
            self.logger.info(f"Sent heartbeat for {self.service_name}")

    @async_retry(max_attempts=5, delay=2)
    async def deregister(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/deregister/{self.service_name}", headers=headers
            )
            resp.raise_for_status()
            self.logger.info(f"Deregistered service {self.service_name}")
