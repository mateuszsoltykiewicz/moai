"""
Audit API Router with async DB integration.

- Logs and queries audit events in a persistent database.
- Uses SQLAlchemy async ORM and Pydantic schemas.
- All endpoints are secured and support filtering.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from datetime import datetime
from typing import List, Optional

from AppLib.models.schemas import AuditEvent, AuditEventCreate
from AppLib.models.audit import AuditEventDB
from db.session import get_db
from api.dependencies import get_current_user
from api.main import APIException

router = APIRouter(tags=["audit"])

@router.get(
    "/",
    response_model=List[AuditEvent],
    summary="List audit events",
    description="Retrieve audit events, optionally filtered by user or action."
)
async def list_audit_events(
    user_filter: Optional[str] = Query(None, alias="user", description="Filter by user"),
    action_filter: Optional[str] = Query(None, alias="action", description="Filter by action"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of events to return"),
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    """
    List audit events with optional filtering.
    """
    try:
        stmt = select(AuditEventDB)
        if user_filter:
            stmt = stmt.where(AuditEventDB.user == user_filter)
        if action_filter:
            stmt = stmt.where(AuditEventDB.action == action_filter)
        stmt = stmt.order_by(AuditEventDB.timestamp.desc()).limit(limit)
        result = await db.execute(stmt)
        events = result.scalars().all()
        return [AuditEvent(**event.__dict__) for event in events]
    except SQLAlchemyError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )

@router.post(
    "/",
    response_model=AuditEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Create audit event"
)
async def create_audit_event(
    event: AuditEventCreate,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Create a new audit event.
    """
    try:
        new_event = AuditEventDB(
            id=str(uuid4()),
            user=user.get("username", "unknown"),
            action=event.action,
            resource=event.resource,
            timestamp=datetime.utcnow(),
            details=event.details
        )
        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)
        return AuditEvent(**new_event.__dict__)
    except SQLAlchemyError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )

@router.get(
    "/{event_id}",
    response_model=AuditEvent,
    summary="Get audit event by ID"
)
async def get_audit_event(
    event_id: str,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Retrieve a single audit event by its ID.
    """
    try:
        result = await db.execute(select(AuditEventDB).where(AuditEventDB.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Audit event not found",
                details={"event_id": event_id}
            )
        return AuditEvent(**event.__dict__)
    except SQLAlchemyError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(e)}
        )
