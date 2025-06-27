"""
API endpoints for DatabaseManager.
"""

from fastapi import APIRouter, HTTPException, Body, Path, Query
from .manager import DatabaseManager
from .schemas import DatabaseRecordCreate, DatabaseRecordResponse
from .exceptions import DatabaseError, RecordNotFoundError, TableNotConfiguredError

router = APIRouter(prefix="/database", tags=["database"])

database_manager: DatabaseManager = None  # Should be initialized at app startup

@router.post("/{table_name}", response_model=DatabaseRecordResponse)
async def create_record(
    table_name: str = Path(..., description="Target table name"),
    record: DatabaseRecordCreate = Body(...)
):
    try:
        return await database_manager.create_record(table_name, record.data)
    except TableNotConfiguredError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/{table_name}/{record_id}", response_model=DatabaseRecordResponse)
async def get_record(
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID")
):
    try:
        return await database_manager.get_record(table_name, record_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{table_name}", response_model=list[DatabaseRecordResponse])
async def list_records(
    table_name: str = Path(..., description="Target table name"),
    limit: int = Query(100, ge=1, le=1000)
):
    return await database_manager.query_records(table_name, limit=limit)

@router.put("/{table_name}/{record_id}", response_model=DatabaseRecordResponse)
async def update_record(
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID"),
    data: dict = Body(...)
):
    try:
        return await database_manager.update_record(table_name, record_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{table_name}/{record_id}", status_code=204)
async def delete_record(
    table_name: str = Path(..., description="Target table name"),
    record_id: str = Path(..., description="Record ID")
):
    try:
        await database_manager.delete_record(table_name, record_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
