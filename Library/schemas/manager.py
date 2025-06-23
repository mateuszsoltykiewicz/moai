"""
SchemasManager: Centralized Pydantic schema management.

- Registers and provides access to all Pydantic schemas used in the application
- Supports schema validation, versioning, and dynamic loading
- Integrates with API documentation and other components
"""

from .registry import schema_registry
from .exceptions import SchemaNotFoundError
from .metrics import record_schema_operation

class SchemasManager:
    """
    Central manager for all schemas in the application.
    """
    def __init__(self):
        self._registry = schema_registry

    async def get_schema(self, name: str):
        """
        Retrieve a registered schema by name.

        Args:
            name: The schema name (string)

        Returns:
            The Pydantic schema class

        Raises:
            SchemaNotFoundError: If schema is not found
        """
        if name not in self._registry:
            raise SchemaNotFoundError(f"Schema '{name}' not found")
        record_schema_operation("get")
        return self._registry[name]

    async def list_schemas(self):
        """
        List all registered schema names.

        Returns:
            List of schema names (strings)
        """
        record_schema_operation("list")
        return list(self._registry.keys())
