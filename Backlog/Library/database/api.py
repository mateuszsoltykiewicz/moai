"""
API endpoints for DatabaseManager.
"""

from fastapi import APIRouter, HTTPException, Body, Path, Query, Depends, Request
from .manager import DatabaseManager
from .schemas import DatabaseRecordCreate, DatabaseRecordResponse
from .exceptions import DatabaseError, RecordNotFoundError, TableNotConfiguredError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/database", tags=["database"])

database_manager: DatabaseManager = None  # Should be initialized at app startup

@router.post("/{table_name}", response_model=DatabaseRecordResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "database", "write"))])
async def create_record(
    request: Request,
    table_name: str = Path(..., description="Target table name"),
    record: DatabaseRecordCreate = Body(...)
):
    try:
        return await database_manager.create_record(table_name, record.data)
    except TableNotConfiguredError as e:
        logger.warning(f"Table not configured: {table_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error on create_record: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/{table_name}/{record_id}", response_model=DatabaseRecordResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "database", "read"))])
async def get_record(
    request: Request,
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID")
):
    try:
        return await database_manager.get_record(table_name, record_id)
    except RecordNotFoundError as e:
        logger.warning(f"Record not found: {record_id} in table {table_name}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{table_name}", response_model=list[DatabaseRecordResponse], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "database", "read"))])
async def list_records(
    request: Request,
    table_name: str = Path(..., description="Target table name"),
    limit: int = Query(100, ge=1, le=1000)
):
    return await database_manager.query_records(table_name, limit=limit)

@router.put("/{table_name}/{record_id}", response_model=DatabaseRecordResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "database", "write"))])
async def update_record(
    request: Request,
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID"),
    data: dict = Body(...)
):
    try:
        return await database_manager.update_record(table_name, record_id, data)
    except RecordNotFoundError as e:
        logger.warning(f"Record not found for update: {record_id} in table {table_name}")
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{table_name}/{record_id}", status_code=204, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "database", "delete"))])
async def delete_record(
    request: Request,
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID")
):
    try:
        await database_manager.delete_record(table_name, record_id)
    except RecordNotFoundError as e:
        logger.warning(f"Record not found for delete: {record_id} in table {table_name}")
        raise HTTPException(status_code=404, detail=str(e))
