# /Python/libraries/core/async_vault_client/__init__.py
import httpx

async def get_secret(vault_url, token, secret_path):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{vault_url}/v1/{secret_path}", headers={"X-Vault-Token": token})
        resp.raise_for_status()
        return resp.json()["data"]["data"]
