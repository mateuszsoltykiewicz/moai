from fastapi import APIRouter, HTTPException, Depends, Request
from .manager import SchemasManager
from .exceptions import SchemaNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

def create_router(manager: SchemasManager) -> APIRouter:
    router = APIRouter(prefix="/schemas", tags=["schemas"])

    @router.get("/", response_model=list[str], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "schemas", "read"))])
    async def list_schemas():
        try:
            return await manager.list_schemas()
        except Exception as e:
            logger.error(f"Failed to list schemas: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")

    @router.get("/{schema_name}", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "schemas", "read"))])
    async def get_schema(schema_name: str):
        try:
            schema_cls = await manager.get_schema(schema_name)
            return schema_cls.schema()
        except SchemaNotFoundError as e:
            logger.warning(f"Schema not found: {schema_name}")
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Failed to get schema: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")

    return router
