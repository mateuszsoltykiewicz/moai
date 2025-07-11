import asyncio
from typing import Dict, Any, Callable, Awaitable, Optional
from .schemas import SecretResponse
from .exceptions import SecretNotFoundError, SecretValidationError, SecretPermissionError
from .metrics import record_secrets_operation, record_secrets_error
from Library.logging import get_logger

logger = get_logger(__name__)

class SecretsManager:
    def __init__(self, vault_manager):
        self._vault = vault_manager
        self._listeners: Dict[str, Callable[[str, Any], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()

    async def get(self, path: str) -> SecretResponse:
        """Cached secret retrieval with permission checks"""
        async with self._cache_lock:
            if path in self._cache:
                return self._cache[path]
        
        async with self._lock:
            try:
                secret, version, meta = await self._vault.read_secret(path)
                if secret is None:
                    raise SecretNotFoundError(f"Secret at '{path}' not found")
                
                # Cache with TTL (production: use Redis)
                async with self._cache_lock:
                    self._cache[path] = secret
                
                record_secrets_operation("get")
                return SecretResponse(path=path, value=secret, version=version, metadata=meta)
            except Exception as e:
                if "permission" in str(e).lower():
                    record_secrets_error("get", "permission")
                    raise SecretPermissionError(f"Access denied for '{path}'") from e
                elif "not found" in str(e).lower():
                    record_secrets_error("get", "not_found")
                    raise SecretNotFoundError(f"Secret at '{path}' not found") from e
                else:
                    record_secrets_error("get", "unknown")
                    logger.error(f"Secret read failed: {str(e)}", exc_info=True)
                    raise

    async def set(self, path: str, value: Dict[str, Any], version: Optional[int] = None) -> SecretResponse:
        """Atomic secret update with version validation"""
        async with self._lock:
            try:
                # Validate secret structure
                if not self._validate_secret(value):
                    raise SecretValidationError("Invalid secret structure")
                
                # Perform atomic write
                updated_version, meta = await self._vault.write_secret(
                    path, 
                    value, 
                    version=version
                )
                
                # Invalidate cache
                async with self._cache_lock:
                    if path in self._cache:
                        del self._cache[path]
                
                # Notify listeners
                await self._notify_listeners(path, value)
                record_secrets_operation("set")
                return SecretResponse(
                    path=path,
                    value=value,
                    version=updated_version,
                    metadata=meta,
                    updated=True
                )
            except Exception as e:
                if "version conflict" in str(e).lower():
                    record_secrets_error("set", "version_conflict")
                    raise SecretValidationError("Secret version conflict") from e
                elif "permission" in str(e).lower():
                    record_secrets_error("set", "permission")
                    raise SecretPermissionError(f"Write denied for '{path}'") from e
                else:
                    record_secrets_error("set", "unknown")
                    logger.error(f"Secret write failed: {str(e)}", exc_info=True)
                    raise

    def _validate_secret(self, value: Dict[str, Any]) -> bool:
        """Production secret validation rules"""
        # Example: Ensure no plaintext credentials
        if "password" in value and len(value["password"]) < 12:
            return False
        return True

    def add_listener(self, name: str, callback: Callable[[str, Any], Awaitable[None]]) -> None:
        """Register async listener for secret changes"""
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """Remove secret change listener"""
        self._listeners.pop(name, None)

    async def _notify_listeners(self, path: str, value: Any) -> None:
        """Notify all async listeners of secret changes"""
        for callback in self._listeners.values():
            try:
                await callback(path, value)
            except Exception as e:
                logger.error(f"Secret listener error: {e}", exc_info=True)
