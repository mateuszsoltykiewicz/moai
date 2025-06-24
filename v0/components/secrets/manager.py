"""
AppLib.services.secrets.manager

Production-ready asynchronous SecretsManager with:
- HashiCorp Vault integration (KV v2 and dynamic DB)
- Token renewal/auto-refresh
- Fallback to env vars or local JSON file
- Rotation notification callback
- Clean shutdown and background task management
"""

import aiohttp
import asyncio
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Awaitable
from AppLib.utils.logger import get_logger

logger = get_logger(__name__)

class VaultConfig:
    def __init__(
        self,
        address: str,
        token: str,
        secrets_path: str,
        verify_ssl: bool = True,
        fallback_json: Optional[str] = None
    ):
        self.address = address.rstrip("/")
        self.token = token
        self.secrets_path = secrets_path.strip("/")
        self.verify_ssl = verify_ssl
        self.fallback_json = fallback_json

class SecretsManager:
    """
    Async secrets manager for Vault with token renewal, fallback, and notification.
    """
    def __init__(
        self,
        config: VaultConfig,
        auto_renew_token: bool = True,
        on_rotate: Optional[Callable[[str, Any], Awaitable[None]]] = None,
        fallback_json: Optional[str] = None,
    ):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._secrets_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._auto_renew_token = auto_renew_token
        self._renew_task: Optional[asyncio.Task] = None
        self._on_rotate = on_rotate
        self._fernet_key: Optional[bytes] = None
        self._fallback_json = fallback_json

    async def __aenter__(self):
        if self._auto_renew_token:
            await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def fetch_secret(self, key: str) -> Any:
        """
        Fetch a secret by key, with cache, Vault, and fallback support.
        """
        async with self._lock:
            if key in self._secrets_cache:
                return self._secrets_cache[key]
            try:
                secret = await self._fetch_secret_from_vault(key)
            except Exception as e:
                logger.warning(f"Vault unavailable, using fallback for {key}: {e}")
                secret = self._fetch_secret_from_env_or_file(key)
            self._secrets_cache[key] = secret
            return secret

    async def _fetch_secret_from_vault(self, key: str) -> Any:
        """
        Internal: Fetch secret from Vault KV v2.
        """
        url = f"{self.config.address}/v1/{self.config.secrets_path}/data/{key}"
        headers = {"X-Vault-Token": self.config.token}
        session = await self._get_session()
        async with session.get(url, headers=headers, ssl=self.config.verify_ssl) as resp:
            if resp.status != 200:
                raise Exception(f"Vault error: HTTP {resp.status} for key {key}")
            data = await resp.json()
            secret = data["data"]["data"]
            logger.debug(f"Fetched secret for key {key} from Vault.")
            return secret

    def _fetch_secret_from_env_or_file(self, key: str) -> Any:
        """
        Fallback: Try environment variable, then local JSON file.
        """
        env_key = f"SECRET_{key.upper()}"
        if env_key in os.environ:
            logger.info(f"Loaded secret {key} from environment variable.")
            return os.environ[env_key]
        if self.config.fallback_json and Path(self.config.fallback_json).exists():
            with open(self.config.fallback_json) as f:
                data = json.load(f)
                if key in data:
                    logger.info(f"Loaded secret {key} from fallback JSON file.")
                    return data[key]
        raise Exception(f"Secret {key} not found in environment or fallback file.")

    async def rotate_secret(self, key: str):
        """
        Force refresh a secret from Vault and notify callback.
        """
        async with self._lock:
            secret = await self._fetch_secret_from_vault(key)
            self._secrets_cache[key] = secret
            logger.info(f"Secret for key {key} rotated.")
            if self._on_rotate:
                await self._on_rotate(key, secret)

    async def get_all_secrets(self) -> Dict[str, Any]:
        """
        Fetch all secrets from Vault path (for bulk loading at startup).
        """
        url = f"{self.config.address}/v1/{self.config.secrets_path}/data"
        headers = {"X-Vault-Token": self.config.token}
        session = await self._get_session()
        async with session.get(url, headers=headers, ssl=self.config.verify_ssl) as resp:
            if resp.status != 200:
                raise Exception(f"Vault error: HTTP {resp.status} for all secrets")
            data = await resp.json()
            secrets = data["data"]["data"]
            async with self._lock:
                self._secrets_cache.update(secrets)
            logger.info("Fetched all secrets from Vault.")
            return secrets

    async def fetch_dynamic_db_creds(self, db_role: str) -> Dict[str, Any]:
        """
        Fetch dynamic DB credentials from Vault's database secrets engine.
        """
        url = f"{self.config.address}/v1/database/creds/{db_role}"
        headers = {"X-Vault-Token": self.config.token}
        session = await self._get_session()
        async with session.get(url, headers=headers, ssl=self.config.verify_ssl) as resp:
            if resp.status != 200:
                logger.error(f"Vault returned HTTP {resp.status} for DB creds")
                raise Exception(f"Vault error: {resp.status}")
            data = await resp.json()
            logger.info(f"Fetched dynamic DB credentials for role {db_role}")
            return data["data"]

    async def start(self):
        """Start background token renewal if enabled."""
        if self._auto_renew_token and not self._renew_task:
            self._renew_task = asyncio.create_task(self._renew_token_loop())

    async def stop(self):
        """Stop background tasks and close session."""
        if self._renew_task:
            self._renew_task.cancel()
            try:
                await self._renew_task
            except asyncio.CancelledError:
                pass
            self._renew_task = None
        await self.close()

    async def _renew_token_loop(self, interval: int = 600):
        """Periodically renew the Vault token."""
        while True:
            await asyncio.sleep(interval)
            try:
                await self.renew_token()
            except Exception as e:
                logger.error(f"Vault token renewal failed: {e}")

    async def renew_token(self):
        """Renew the Vault token (if allowed)."""
        url = f"{self.config.address}/v1/auth/token/renew-self"
        headers = {"X-Vault-Token": self.config.token}
        session = await self._get_session()
        async with session.post(url, headers=headers, ssl=self.config.verify_ssl) as resp:
            if resp.status != 200:
                raise Exception(f"Vault token renewal failed: HTTP {resp.status}")
            logger.info("Vault token renewed successfully.")

    async def get_encryption_key(self) -> bytes:
        """Retrieve or generate encryption key"""
        if not self._fernet_key:
            if self.config.encryption.existing_key:
                self._fernet_key = self.config.encryption.existing_key.encode()
            else:
                self._fernet_key = Fernet.generate_key()
                logger.info("Generated new encryption key")
        return self._fernet_key

    async def close(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
