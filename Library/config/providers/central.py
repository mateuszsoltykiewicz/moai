import httpx
import websockets
from ..provider import ConfigProvider

class CentralConfigProvider(ConfigProvider):
    def __init__(self, server_url: str, service_name: str, env: str):
        self.server_url = server_url
        self.service_name = service_name
        self.env = env
        self.ws = None

    async def setup(self):
        pass

    async def teardown(self):
        if self.ws:
            await self.ws.close()

    async def load(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/config/{self.service_name}/{self.env}"
            )
            response.raise_for_status()
            return response.json()["config"]

    async def watch(self):
        async with websockets.connect(f"{self.server_url}/ws") as ws:
            self.ws = ws
            while True:
                await ws.recv()
                yield
