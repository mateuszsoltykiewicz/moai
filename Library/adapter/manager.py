"""
AdapterManager: Centralized async adapter management.

- Manages registration, retrieval, and lifecycle of hardware/software adapters
- Supports dynamic adapter loading based on configuration
- Integrates with sessions, metrics, and logging
"""

from typing import Dict, Any, Type, Optional
import asyncio
from .registry import adapter_registry
from .exceptions import AdapterNotFoundError
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

        Args:
            adapter_type: The adapter type (e.g., "i2c", "canbus", "kafka")
            config: Configuration for the adapter

        Returns:
            The adapter instance

        Raises:
            AdapterNotFoundError: If adapter type is not found
        """
        async with self._lock:
            if adapter_type not in self._registry:
                raise AdapterNotFoundError(f"Adapter type '{adapter_type}' not found")
            if adapter_type not in self._adapters:
                adapter_cls = self._registry[adapter_type]
                self._adapters[adapter_type] = adapter_cls(config)
                log_info(f"AdapterManager: Created adapter {adapter_type}")
                record_adapter_operation("create")
            return self._adapters[adapter_type]

    async def register_adapter(self, adapter_type: str, adapter_cls: Type) -> None:
        """
        Register a new adapter class.

        Args:
            adapter_type: The adapter type (e.g., "i2c", "canbus", "kafka")
            adapter_cls: The adapter class to register
        """
        async with self._lock:
            self._registry[adapter_type] = adapter_cls
            log_info(f"AdapterManager: Registered adapter {adapter_type}")
            record_adapter_operation("register")

    async def list_adapters(self) -> Dict[str, str]:
        """
        List all registered adapter types.

        Returns:
            Dict[str, str]: Adapter type -> class name
        """
        async with self._lock:
            return {k: v.__name__ for k, v in self._registry.items()}
