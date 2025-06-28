import asyncio
from typing import Dict, Type, List
from pydantic import BaseModel
from .exceptions import SchemaNotFoundError
from .metrics import record_schema_operation
from Library.logging import get_logger

logger = get_logger(__name__)

class SchemasManager:
    def __init__(self):
        self._registry: Dict[str, Type[BaseModel]] = {}
        self._lock = asyncio.Lock()

    def register_schema(self, name: str, schema_cls: Type[BaseModel]) -> None:
        """Register a schema at startup"""
        with self._lock:
            if name in self._registry:
                logger.warning(f"Schema '{name}' already registered - overwriting")
            self._registry[name] = schema_cls
            logger.info(f"Registered schema: {name}")

    async def list_schemas(self) -> List[str]:
        """List all registered schema names"""
        with self._lock:
            record_schema_operation("list")
            return list(self._registry.keys())

    async def get_schema(self, name: str) -> Type[BaseModel]:
        """Get schema class by name"""
        with self._lock:
            if name not in self._registry:
                logger.error(f"Schema '{name}' not found")
                raise SchemaNotFoundError(f"Schema '{name}' not found")
            record_schema_operation("get")
            return self._registry[name]
