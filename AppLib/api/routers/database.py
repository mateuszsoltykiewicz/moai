"""
Database API Router (Production-Grade)

- Async CRUD endpoints with RBAC security
- Pre/post hooks for validation and auditing
- Comprehensive observability (tracing, metrics, logging)
- SQLAlchemy async ORM integration
- Pydantic schemas for request/response
- Error handling with custom exceptions
"""

from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from typing import List, Dict, Any
from core.tracing import AsyncTracer
from metrics.database import record_database_operation
from core.logging import logger
from api.dependencies import base_endpoint_processor, require_role, get_db_session
from exceptions.core import NotFoundError, ServiceUnavailableError
from models.database import DatabaseRecordDB
from schemas.database import DatabaseRecordCreate, DatabaseRecordResponse
import time

# Initialize tracer
tracer = AsyncTracer("applib-database").get_tracer()

router = APIRouter(
    prefix="/database",
    tags=["database"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        503: {"description": "Service Unavailable"}
    }
)

@router.post(
    "",
    response_model=DatabaseRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new record"
)
async def create_record(
    record: DatabaseRecordCreate = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="database:create",
            pre_hook="api.hooks.database.validate_create",
            post_hook="api.hooks.database.audit_create",
            dependencies=[Depends(require_role("database.create"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Create new database record with:
    - RBAC enforcement
    - Validation and audit hooks
    - Async DB persistence
    - Tracing and metrics
    """
    start_time = time.monotonic()
    try:
        # Pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        
        with tracer.start_as_current_span("database_create"):
            new_rec = DatabaseRecordDB(id=str(uuid4()), data=record.data)
            db.add(new_rec)
            await db.commit()
            await db.refresh(new_rec)
        
        duration = time.monotonic() - start_time
        record_database_operation("create", duration)
        logger.info(f"Record created by {context['user'].sub}: {new_rec.id}")
        
        return DatabaseRecordResponse(id=new_rec.id, data=new_rec.data)
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise ServiceUnavailableError("Database service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

@router.get(
    "",
    response_model=List[DatabaseRecordResponse],
    summary="List all records"
)
async def list_records(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="database:list",
            dependencies=[Depends(require_role("database.read"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    List all database records with RBAC
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("database_list"):
            result = await db.execute(select(DatabaseRecordDB))
            records = result.scalars().all()
            response = [DatabaseRecordResponse(id=rec.id, data=rec.data) for rec in records]
        
        duration = time.monotonic() - start_time
        record_database_operation("list", duration, count=len(records))
        logger.info(f"Listed {len(records)} records")
        
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise ServiceUnavailableError("Database service unavailable")

@router.get(
    "/{record_id}",
    response_model=DatabaseRecordResponse,
    summary="Get record by ID"
)
async def get_record(
    record_id: str,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="database:get",
            dependencies=[Depends(require_role("database.read"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Get database record by ID with RBAC
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("database_get"):
            result = await db.execute(select(DatabaseRecordDB).where(DatabaseRecordDB.id == record_id))
            rec = result.scalar_one_or_none()
            if not rec:
                raise NotFoundError(f"Record {record_id} not found")
        
        duration = time.monotonic() - start_time
        record_database_operation("get", duration)
        logger.info(f"Fetched record {record_id}")
        
        return DatabaseRecordResponse(id=rec.id, data=rec.data)
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise ServiceUnavailableError("Database service unavailable")

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete record by ID"
)
async def delete_record(
    record_id: str,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="database:delete",
            dependencies=[Depends(require_role("database.delete"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Delete database record by ID with RBAC
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("database_delete"):
            result = await db.execute(select(DatabaseRecordDB).where(DatabaseRecordDB.id == record_id))
            rec = result.scalar_one_or_none()
            if not rec:
                raise NotFoundError(f"Record {record_id} not found")
            await db.delete(rec)
            await db.commit()
        
        duration = time.monotonic() - start_time
        record_database_operation("delete", duration)
        logger.info(f"Deleted record {record_id}")
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise ServiceUnavailableError("Database service unavailable")
