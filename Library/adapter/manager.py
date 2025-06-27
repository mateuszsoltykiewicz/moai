"""
AdapterManager: Centralized async adapter management.

- Manages registration, retrieval, and lifecycle of hardware/software adapters
- Supports dynamic adapter loading based on configuration
- Integrates with metrics and logging
"""

from typing import Dict, Any, Type, Optional
import asyncio
from .registry import adapter_registry
from .exceptions import AdapterNotFoundError, AdapterCreationError
from .metrics import record_adapter_operation
from .utils import log_info

class AdapterManager:
    """
    Central manager for all adapters in the application.
    """
    def __init__(self):
        self._adapters: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._registry = adapter_registry

    async def get_adapter(self, adapter_type: str, config: Dict[str, Any]) -> Any:
        """
        Get or create an adapter instance by type and config.
        """
        async with self._lock:
            if adapter_type not in self._registry:
                record_adapter_operation("get", adapter_type, "not_found")
                raise AdapterNotFoundError(f"Adapter type '{adapter_type}' not found")
            if adapter_type not in self._adapters:
                adapter_cls = self._registry[adapter_type]
                try:
                    adapter = adapter_cls(config)
                    # If the adapter has an async setup, call it
                    if hasattr(adapter, "async_setup"):
                        await adapter.async_setup()
                    self._adapters[adapter_type] = adapter
                    log_info(f"AdapterManager: Created adapter {adapter_type}")
                    record_adapter_operation("create", adapter_type, "success")
                except Exception as e:
                    log_info(f"AdapterManager: Failed to create adapter {adapter_type}: {e}")
                    record_adapter_operation("create", adapter_type, "failed")
                    raise AdapterCreationError(f"Failed to create {adapter_type}: {e}") from e
            return self._adapters[adapter_type]

    async def register_adapter(self, adapter_type: str, adapter_cls: Type) -> None:
        """
        Register a new adapter class.
        """
        async with self._lock:
            self._registry[adapter_type] = adapter_cls
            log_info(f"AdapterManager: Registered adapter {adapter_type}")
            record_adapter_operation("register", adapter_type, "success")

    async def list_adapters(self) -> Dict[str, str]:
        """
        List all registered adapter types.
        """
        async with self._lock:
            return {k: v.__name__ for k, v in self._registry.items()}

    async def shutdown(self):
        """
        Gracefully shutdown all adapters (call async_teardown if available).
        """
        async with self._lock:
            for name, adapter in self._adapters.items():
                if hasattr(adapter, "async_teardown"):
                    await adapter.async_teardown()
                log_info(f"AdapterManager: Shutdown adapter {name}")
            self._adapters.clear()
