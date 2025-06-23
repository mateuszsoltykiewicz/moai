"""
API endpoints for DatabaseManager.

- Exposes /database/ for CRUD operations
"""

from fastapi import APIRouter, HTTPException, Body
from .manager import DatabaseManager
from .schemas import DatabaseRecordCreate, DatabaseRecordResponse
from .exceptions import DatabaseError, RecordNotFoundError

router = APIRouter(prefix="/database", tags=["database"])

database_manager: DatabaseManager = None  # Should be initialized at app startup

@router.post("/", response_model=DatabaseRecordResponse)
async def create_record(req: DatabaseRecordCreate = Body(...)):
    """
    Create a new record.
    """
    try:
        return await database_manager.create_record(req)
    except DatabaseError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/{record_id}", response_model=DatabaseRecordResponse)
async def get_record(record_id: str):
    """
    Get a record by ID.
    """
    try:
        return await database_manager.get_record(record_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[DatabaseRecordResponse])
async def list_records():
    """
    List all records.
    """
    return await database_manager.list_records()

@router.put("/{record_id}", response_model=DatabaseRecordResponse)
async def update_record(record_id: str,  dict = Body(...)):
    """
    Update a record by ID.
    """
    try:
        return await database_manager.update_record(record_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{record_id}", status_code=204)
async def delete_record(record_id: str):
    """
    Delete a record by ID.
    """
    try:
        await database_manager.delete_record(record_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
