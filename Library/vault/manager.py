"""
VaultManager: Async client for HashiCorp Vault.

- Manages secrets, tokens, and authentication
- Handles async read/write/delete operations
- Supports token renewal and error handling
- Integrates with metrics and tracing
"""

import asyncio
import hvac
from typing import Dict, Any, Optional, Tuple
from .schemas import VaultSecretResponse, VaultTokenResponse
from .exceptions import VaultError, VaultNotFoundError
from .metrics import record_vault_operation
from .utils import log_info

class VaultManager:
    def __init__(self, addr: str, token: str, namespace: Optional[str] = None):
        self._addr = addr
        self._token = token
        self._namespace = namespace
        self._client = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """Async connect to Vault."""
        try:
            self._client = hvac.Client(
                url=self._addr,
                token=self._token,
                namespace=self._namespace
            )
            if not self._client.is_authenticated():
                raise VaultError("Vault authentication failed")
            log_info("VaultManager: Connected to Vault")
        except Exception as e:
            raise VaultError(f"Vault connection error: {e}")

    async def read_secret(self, path: str) -> Tuple[Dict[str, Any], int]:
        """
        Read a secret from Vault.
        """
        async with self._lock:
            if self._client is None:
                await self.connect()
            try:
                secret = self._client.secrets.kv.v2.read_secret_version(path=path)
                if not secret or "data" not in secret or "data" not in secret["data"]:
                    raise VaultNotFoundError(f"Secret not found at {path}")
                record_vault_operation("read")
                log_info(f"VaultManager: Read secret at {path}")
                return secret["data"]["data"], secret["data"]["metadata"]["version"]
            except Exception as e:
                raise VaultError(f"Vault read error: {e}")

    async def write_secret(
        self, 
        path: str, 
        data: Dict[str, Any], 
        version: Optional[int] = None
    ) -> int:
        """
        Write a secret to Vault.

        Args:
            path: Vault secret path
             Secret data as key-value pairs
            version: Optional version for CAS (Check-And-Set) operations

        Returns:
            New version number of the secret
        """
        async with self._lock:
            if self._client is None:
                await self.connect()
            try:
                params = {}
                if version is not None:
                    params["cas"] = version

                secret = self._client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=data,
                    **params
                )
                record_vault_operation("write")
                log_info(f"VaultManager: Wrote secret at {path}")
                return secret["data"]["version"]
            except Exception as e:
                raise VaultError(f"Vault write error: {e}")

    async def delete_secret(self, path: str) -> None:
        """
        Delete a secret from Vault.
        """
        async with self._lock:
            if self._client is None:
                await self.connect()
            try:
                self._client.secrets.kv.v2.delete_metadata_and_all_versions(path)
                record_vault_operation("delete")
                log_info(f"VaultManager: Deleted secret at {path}")
            except Exception as e:
                raise VaultError(f"Vault delete error: {e}")

    async def renew_token(self) -> None:
        """
        Renew Vault token.
        """
        async with self._lock:
            if self._client is None:
                await self.connect()
            try:
                self._client.auth.token.renew_self()
                record_vault_operation("renew")
                log_info("VaultManager: Token renewed")
            except Exception as e:
                raise VaultError(f"Vault token renewal error: {e}")
