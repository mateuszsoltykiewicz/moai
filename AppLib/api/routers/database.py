"""
Database API Router

- Async CRUD endpoints for generic records.
- Uses SQLAlchemy async ORM and Pydantic schemas.
- All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from typing import List

from models.database import DatabaseRecordDB
from AppLib.models.schemas import DatabaseRecordCreate, DatabaseRecordResponse
from sessions.database import get_db_session
from api.dependencies import get_current_user
from api.main import APIException

router = APIRouter(tags=["database"])

@router.post(
    "/",
    response_model=DatabaseRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new record"
)
async def create_record(
    record: DatabaseRecordCreate,
    db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    try:
        new_rec = DatabaseRecordDB(id=str(uuid4()), data=record.data)
        db.add(new_rec)
        await db.commit()
        await db.refresh(new_rec)
        return DatabaseRecordResponse(id=new_rec.id, data=new_rec.data)
    except SQLAlchemyError as e:
        await db.rollback()
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )

@router.get(
    "/",
    response_model=List[DatabaseRecordResponse],
    summary="List all records"
)
async def list_records(
    db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    try:
        result = await db.execute(select(DatabaseRecordDB))
        return [DatabaseRecordResponse(id=rec.id, data=rec.data) for rec in result.scalars()]
    except SQLAlchemyError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )

@router.get(
    "/{record_id}",
    response_model=DatabaseRecordResponse,
    summary="Get record by ID"
)
async def get_record(
    record_id: str,
    db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    try:
        result = await db.execute(select(DatabaseRecordDB).where(DatabaseRecordDB.id == record_id))
        rec = result.scalar_one_or_none()
        if not rec:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Record not found",
                details={"record_id": record_id}
            )
        return DatabaseRecordResponse(id=rec.id, data=rec.data)
    except SQLAlchemyError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete record by ID"
)
async def delete_record(
    record_id: str,
    db=Depends(get_db_session),
    user=Depends(get_current_user)
):
    try:
        result = await db.execute(select(DatabaseRecordDB).where(DatabaseRecordDB.id == record_id))
        rec = result.scalar_one_or_none()
        if not rec:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Record not found",
                details={"record_id": record_id}
            )
        await db.delete(rec)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )
