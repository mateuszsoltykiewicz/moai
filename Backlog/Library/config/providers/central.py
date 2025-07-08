import httpx
import websockets
from ..provider import ConfigProvider
from Library.logging import get_logger

logger = get_logger(__name__)

class CentralConfigProvider(ConfigProvider):
    def __init__(self, server_url: str, service_name: str, env: str):
        self.server_url = server_url
        self.service_name = service_name
        self.env = env
        self.ws = None

    async def setup(self):
        logger.info(f"Connecting to central config server: {self.server_url}")

    async def teardown(self):
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from central config server")

    async def load(self) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/config/{self.service_name}/{self.env}"
                )
                response.raise_for_status()
                logger.debug(f"Loaded config from central server: {self.server_url}")
                return response.json()["config"]
        except Exception as e:
            logger.error(f"Failed to load config from central server: {e}", exc_info=True)
            raise

    async def watch(self):
        try:
            async with websockets.connect(f"{self.server_url}/ws") as ws:
                self.ws = ws
                logger.info("Watching for config changes via WebSocket")
                while True:
                    await ws.recv()
                    yield
        except Exception as e:
            logger.error(f"Config watch failed: {e}", exc_info=True)
            raise
