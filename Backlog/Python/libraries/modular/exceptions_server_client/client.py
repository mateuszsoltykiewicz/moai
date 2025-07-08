import httpx
from core.async_logging import setup_async_logger
from core.async_retry_helpers import async_retry

class ExceptionsServerClient:
    def __init__(self, base_url, token, logger=None):
        self.base_url = base_url
        self.token = token
        self.logger = logger or setup_async_logger("exceptions_server_client")

    @async_retry(max_attempts=5, delay=2)
    async def publish_exception(self, exception_event):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/exceptions", json=exception_event, headers=headers
            )
            resp.raise_for_status()
            self.logger.info("Published exception event")
