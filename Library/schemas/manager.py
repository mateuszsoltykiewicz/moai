import asyncio
from typing import List, Type
from .registry import schema_registry
from .exceptions import SchemaNotFoundError
from .metrics import record_schema_operation
from .utils import log_info, log_error

class SchemasManager:
    def __init__(self):
        self._registry = schema_registry
        self._lock = asyncio.Lock()

    async def get_schema(self, name: str) -> Type:
        async with self._lock:
            if name not in self._registry:
                log_error(f"Schema '{name}' not found")
                raise SchemaNotFoundError(f"Schema '{name}' not found")
            record_schema_operation("get")
            log_info(f"Schema '{name}' retrieved")
            return self._registry[name]

    async def list_schemas(self) -> List[str]:
        async with self._lock:
            record_schema_operation("list")
            log_info("Schema list retrieved")
            return list(self._registry.keys())

    async def register_schema(self, name: str, schema_cls: Type) -> None:
        async with self._lock:
            self._registry[name] = schema_cls
            log_info(f"Schema '{name}' registered")
