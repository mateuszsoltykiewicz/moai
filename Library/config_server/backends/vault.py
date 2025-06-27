import asyncio
import hvac
from os import getenv
from .utils import log_error
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential

class VaultSecretBackend:
    def __init__(self, vault_addr: str):
        self.vault_addr = vault_addr
        self.client = hvac.Client(url=vault_addr)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.token = None
        
    async def connect(self):
        """Secure connection with retry"""
        await self._run_in_executor(self._authenticate)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _authenticate(self):
        if not self.client.is_authenticated():
            # Use Kubernetes auth in production
            self.client.auth.approle.login(
                role_id=getenv("VAULT_ROLE_ID"),
                secret_id=getenv("VAULT_SECRET_ID")
            )
            self.token = self.client.token
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get_secret(self, path: str) -> str:
        return await self._run_in_executor(self._fetch_secret, path)
    
    def _fetch_secret(self, path: str) -> str:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point="secret"
            )
            return response["data"]["data"]["value"]
        except hvac.exceptions.InvalidPath:
            log_error(f"Secret path not found: {path}")
            return ""
        except hvac.exceptions.Forbidden:
            log_error(f"Permission denied for secret: {path}")
            self._authenticate()  # Re-authenticate
            return self._fetch_secret(path)
    
    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)
