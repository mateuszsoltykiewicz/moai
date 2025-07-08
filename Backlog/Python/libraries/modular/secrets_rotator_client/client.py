import httpx
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class SecretsRotatorClient:
    def __init__(self, base_url, token, service_name, logger=None):
        self.base_url = base_url
        self.token = token
        self.service_name = service_name
        self.logger = logger or setup_async_logger("secrets_rotator_client")

    @async_retry(max_attempts=5, delay=2)
    async def fetch_secret(self, secret_path):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/secrets/{self.service_name}/{secret_path}", headers=headers
            )
            resp.raise_for_status()
            secret = resp.json()["secret"]
            self.logger.info(f"Fetched secret for {secret_path}")
            return secret

    async def watch_for_rotation(self, callback, poll_interval=60):
        while True:
            try:
                # Poll for secret rotation events or use push-based notifications
                secret = await self.fetch_secret("db_password")
                await callback(secret)
            except Exception as e:
                self.logger.error(f"Secret rotation failed: {e}")
            await asyncio.sleep(poll_interval)
