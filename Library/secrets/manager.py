"""
SecretsManager: Async secret management with Vault integration.

- Manages retrieval, update, and rotation of secrets
- Integrates with VaultManager for backend operations
- Notifies listeners on secret changes
- Exposes metrics for secret operations
"""

import asyncio
from typing import Dict, Any, Callable, Awaitable, Optional
from .schemas import SecretResponse, SecretUpdateRequest
from .exceptions import SecretNotFoundError, SecretValidationError
from .metrics import record_secrets_operation
from .utils import log_info

class SecretsManager:
    def __init__(self, vault_manager):
        self._vault = vault_manager
        self._listeners: Dict[str, Callable[[str, Any], Awaitable[None]]] = {}
        self._lock = asyncio.Lock()

    async def get(self, path: str) -> SecretResponse:
        """
        Retrieve a secret from Vault.
        """
        async with self._lock:
            secret, version = await self._vault.read_secret(path)
            if secret is None:
                raise SecretNotFoundError(f"Secret at path '{path}' not found")
            record_secrets_operation("get")
            log_info(f"SecretsManager: Retrieved secret at {path}")
            return SecretResponse(path=path, value=secret, version=version, updated=False)

    async def set(self, path: str, value: Dict[str, Any], version: Optional[int] = None) -> SecretResponse:
        """
        Set or rotate a secret in Vault.
        """
        async with self._lock:
            updated_version = await self._vault.write_secret(path, value, version=version)
            record_secrets_operation("set")
            log_info(f"SecretsManager: Updated secret at {path}")
            await self._notify_listeners(path, value)
            return SecretResponse(path=path, value=value, version=updated_version, updated=True)

    def add_listener(self, name: str, callback: Callable[[str, Any], Awaitable[None]]) -> None:
        """
        Register async listener for secret changes.
        """
        self._listeners[name] = callback

    def remove_listener(self, name: str) -> None:
        """
        Remove secret change listener.
        """
        self._listeners.pop(name, None)

    async def _notify_listeners(self, path: str, value: Any) -> None:
        """
        Notify all async listeners of secret changes.
        """
        for callback in self._listeners.values():
            try:
                await callback(path, value)
            except Exception as e:
                log_info(f"Secret listener error: {e}")
