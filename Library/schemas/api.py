from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from .manager import SchemasManager
from .exceptions import SchemaNotFoundError
from pydantic import BaseModel

router = APIRouter(prefix="/schemas", tags=["schemas"])

schemas_manager = SchemasManager()

@router.get("/", response_model=list[str])
async def list_schemas():
    """
    List all registered schema names.
    """
    try:
        return await schemas_manager.list_schemas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list schemas: {e}")

@router.get("/{schema_name}")
async def get_schema(schema_name: str):
    """
    Get a schema definition by name.
    """
    try:
        schema_cls = await schemas_manager.get_schema(schema_name)
        return JSONResponse(content=schema_cls.schema())
    except SchemaNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {e}")
