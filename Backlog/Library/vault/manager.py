"""
Production-grade VaultManager with async operations, caching, and enhanced security.
"""

import asyncio
import hvac
from typing import Dict, Any, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import VaultError, VaultNotFoundError, VaultConnectionError, VaultPermissionError
from .metrics import record_vault_operation, record_vault_error
from Library.logging import get_logger
import cachetools
import time

logger = get_logger(__name__)

class VaultManager:
    def __init__(self, addr: str, token: str, namespace: Optional[str] = None):
        self._addr = addr
        self._token = token
        self._namespace = namespace
        self._client = None
        self._lock = asyncio.Lock()
        self._cache = cachetools.TTLCache(maxsize=1000, ttl=60)  # 1 min TTL
        self._last_renewal = 0
        self._token_ttl = 3600  # Default token TTL

    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(VaultConnectionError),
        reraise=True
    )
    async def connect(self) -> None:
        """Secure connection with retry logic"""
        try:
            start_time = time.monotonic()
            self._client = hvac.Client(
                url=self._addr,
                token=self._token,
                namespace=self._namespace,
                timeout=5
            )
            # Verify connection
            if not await self._run_in_executor(self._client.is_authenticated):
                raise VaultConnectionError("Vault authentication failed")
            logger.info("Connected to Vault")
        except (hvac.exceptions.VaultDown, hvac.exceptions.InternalServerError) as e:
            raise VaultConnectionError(f"Connection failed: {e}") from e
        except Exception as e:
            record_vault_error("connect")
            logger.error(f"Vault connection error: {e}", exc_info=True)
            raise

    async def read_secret(self, path: str) -> Tuple[Dict[str, Any], int]:
        """Cached secret retrieval with validation"""
        async with self._lock:
            # Check cache first
            if path in self._cache:
                return self._cache[path]
            
            start_time = time.monotonic()
            try:
                if self._client is None:
                    await self.connect()
                
                secret = await self._run_in_executor(
                    self._client.secrets.kv.v2.read_secret_version,
                    path=path
                )
                
                if not secret or "data" not in secret or "data" not in secret["data"]:
                    raise VaultNotFoundError(f"Secret not found at {path}")
                
                data = secret["data"]["data"]
                version = secret["data"]["metadata"]["version"]
                
                # Validate secret structure
                self._validate_secret(data)
                
                # Update cache
                self._cache[path] = (data, version)
                
                record_vault_operation("read")
                logger.info(f"Read secret at {path}")
                return data, version
            except hvac.exceptions.InvalidPath as e:
                raise VaultNotFoundError(str(e)) from e
            except hvac.exceptions.Forbidden as e:
                raise VaultPermissionError(f"Permission denied for {path}") from e
            except Exception as e:
                record_vault_error("read")
                logger.error(f"Secret read failed: {str(e)}", exc_info=True)
                raise

    async def write_secret(self, path: str, data: Dict[str, Any], version: Optional[int] = None) -> int:
        """Atomic write with validation and cache invalidation"""
        async with self._lock:
            start_time = time.monotonic()
            try:
                # Validate before write
                self._validate_secret(data)
                
                if self._client is None:
                    await self.connect()
                
                params = {"path": path, "secret": data}
                if version is not None:
                    params["cas"] = version
                
                secret = await self._run_in_executor(
                    self._client.secrets.kv.v2.create_or_update_secret,
                    **params
                )
                
                # Invalidate cache
                if path in self._cache:
                    del self._cache[path]
                
                record_vault_operation("write")
                logger.info(f"Wrote secret at {path}")
                return secret["data"]["version"]
            except hvac.exceptions.InvalidPath as e:
                raise VaultNotFoundError(str(e)) from e
            except hvac.exceptions.Forbidden as e:
                raise VaultPermissionError(f"Write denied for {path}") from e
            except Exception as e:
                record_vault_error("write")
                logger.error(f"Secret write failed: {str(e)}", exc_info=True)
                raise

    async def delete_secret(self, path: str) -> None:
        """Secure deletion with cache invalidation"""
        async with self._lock:
            start_time = time.monotonic()
            try:
                if self._client is None:
                    await self.connect()
                
                await self._run_in_executor(
                    self._client.secrets.kv.v2.delete_metadata_and_all_versions,
                    path
                )
                
                # Invalidate cache
                if path in self._cache:
                    del self._cache[path]
                
                record_vault_operation("delete")
                logger.info(f"Deleted secret at {path}")
            except hvac.exceptions.InvalidPath as e:
                raise VaultNotFoundError(str(e)) from e
            except hvac.exceptions.Forbidden as e:
                raise VaultPermissionError(f"Delete denied for {path}") from e
            except Exception as e:
                record_vault_error("delete")
                logger.error(f"Secret delete failed: {str(e)}", exc_info=True)
                raise

    async def renew_token(self) -> Dict[str, Any]:
        """Token renewal with TTL tracking"""
        async with self._lock:
            start_time = time.monotonic()
            try:
                if self._client is None:
                    await self.connect()
                
                # Only renew if token is near expiration
                if time.time() - self._last_renewal < self._token_ttl * 0.8:
                    return {"token": self._token, "renewable": True, "ttl": self._token_ttl}
                
                response = await self._run_in_executor(
                    self._client.auth.token.renew_self
                )
                
                self._token = response["auth"]["client_token"]
                self._token_ttl = response["auth"]["lease_duration"]
                self._last_renewal = time.time()
                
                record_vault_operation("renew")
                logger.info("Token renewed")
                return {
                    "token": self._token,
                    "renewable": response["auth"]["renewable"],
                    "ttl": self._token_ttl
                }
            except Exception as e:
                record_vault_error("renew")
                logger.error(f"Token renewal failed: {str(e)}", exc_info=True)
                raise

    def _validate_secret(self, data: Dict[str, Any]) -> None:
        """Production secret validation rules"""
        if not isinstance(data, dict):
            raise VaultError("Secret must be a dictionary")
        if any(len(k) > 256 for k in data.keys()):
            raise VaultError("Secret key too long (max 256 chars)")
        if any(len(str(v)) > 4096 for v in data.values()):
            raise VaultError("Secret value too large (max 4KB)")
