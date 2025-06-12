import os
import hvac
from typing import Optional

class AsyncVaultAdapter:
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = url or os.environ.get("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.environ.get("VAULT_TOKEN")
        self.client = hvac.AsyncClient(url=self.url, token=self.token)

    async def is_authenticated(self) -> bool:
        return await self.client.is_authenticated()

    async def set_secret(self, path: str, value: dict):
        # path: e.g. "secret/data/my-key"
        await self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=value
        )

    async def get_secret(self, path: str) -> Optional[dict]:
        try:
            result = await self.client.secrets.kv.v2.read_secret_version(path=path)
            return result["data"]["data"]
        except Exception:
            return None

    async def delete_secret(self, path: str):
        await self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
