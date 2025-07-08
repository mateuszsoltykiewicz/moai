# /Python/libraries/modular/async_service_clients/__init__.py
import httpx

class AsyncServiceClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    async def get(self, path):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}{path}", headers={"Authorization": f"Bearer {self.token}"})
            resp.raise_for_status()
            return resp.json()

    async def post(self, path, data):
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}{path}", json=data, headers={"Authorization": f"Bearer {self.token}"})
            resp.raise_for_status()
            return resp.json()
