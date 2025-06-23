"""
API endpoints for SchemasManager.

- Exposes /schemas/ for schema discovery and validation
"""

from fastapi import APIRouter, HTTPException, Query
from .manager import SchemasManager
from .exceptions import SchemaNotFoundError

router = APIRouter(prefix="/schemas", tags=["schemas"])

schemas_manager = SchemasManager()

@router.get("/", response_model=list[str])
async def list_schemas():
    """
    List all registered schema names.
    """
    return await schemas_manager.list_schemas()

@router.get("/{schema_name}")
async def get_schema(schema_name: str):
    """
    Get a schema definition by name.
    """
    try:
        schema_cls = await schemas_manager.get_schema(schema_name)
        return schema_cls.schema()
    except SchemaNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
