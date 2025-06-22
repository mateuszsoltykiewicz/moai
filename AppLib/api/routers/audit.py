"""
Audit API Router

- Async DB integration with SQLAlchemy
- Configurable security (RBAC)
- Pre/post custom hooks
- Default executions
- Comprehensive metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from models.schemas.audit import AuditEventCreate, AuditEventResponse
from api.dependencies import base_endpoint_processor, require_role, get_db_session
from exceptions.core import NotFoundError, ServiceUnavailableError
from core.audit import AuditService
from core.metrics import record_audit_operation
from core.tracing import AsyncTracer
from core.logging import logger

# Instantiate tracer globally or import a singleton if you have one
tracer = AsyncTracer("applib-audit").get_tracer()

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        503: {"description": "Service Unavailable"}
    }
)

@router.post(
    "",
    response_model=AuditEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new audit event"
)
async def create_audit_event(
    event: AuditEventCreate = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="audit:create",
            pre_hook="api.hooks.audit.validate_audit_event",
            post_hook="api.hooks.audit.log_audit_event",
            dependencies=[Depends(require_role("audit.create"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Create a new audit event with:
    - RBAC enforcement
    - Validation and audit logging hooks
    - Async DB persistence
    - Tracing and metrics
    """
    start_time = datetime.utcnow()
    try:
        # Pre-hook validation result
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )

        with tracer.start_as_current_span("audit_create"):
            service = AuditService(db)
            audit_event = await service.create_event(event, context["user"])

        duration = (datetime.utcnow() - start_time).total_seconds()
        record_audit_operation("create", duration)

        logger.info(f"Audit event created by {context['user'].sub} in {duration:.3f}s")
        return audit_event
    except ServiceUnavailableError:
        logger.error("Audit service unavailable during event creation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit service is currently unavailable"
        )

@router.get(
    "",
    response_model=List[AuditEventResponse],
    summary="List audit events"
)
async def list_audit_events(
    user_filter: str = None,
    action_filter: str = None,
    limit: int = 100,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="audit:list",
            dependencies=[Depends(require_role("audit.read"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    List audit events with optional filtering and RBAC
    """
    start_time = datetime.utcnow()
    try:
        with tracer.start_as_current_span("audit_list"):
            service = AuditService(db)
            events = await service.list_events(user_filter, action_filter, limit, context["user"])

        duration = (datetime.utcnow() - start_time).total_seconds()
        record_audit_operation("list", duration, count=len(events))

        logger.info(f"{len(events)} audit events listed by {context['user'].sub} in {duration:.3f}s")
        return events
    except ServiceUnavailableError:
        logger.error("Audit service unavailable during list operation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit service is currently unavailable"
        )

@router.get(
    "/{event_id}",
    response_model=AuditEventResponse,
    summary="Get audit event by ID"
)
async def get_audit_event(
    event_id: UUID,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="audit:get",
            dependencies=[Depends(require_role("audit.read"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Retrieve a single audit event by ID with RBAC
    """
    try:
        with tracer.start_as_current_span("audit_get"):
            service = AuditService(db)
            event = await service.get_event(event_id, context["user"])
            if not event:
                raise NotFoundError(f"Audit event {event_id} not found")
        logger.info(f"Audit event {event_id} retrieved by {context['user'].sub}")
        return event
    except NotFoundError as ne:
        logger.warning(str(ne))
        raise HTTPException(status_code=404, detail=str(ne))
    except ServiceUnavailableError:
        logger.error("Audit service unavailable during get operation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit service is currently unavailable"
        )

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audit event by ID"
)
async def delete_audit_event(
    event_id: UUID,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="audit:delete",
            dependencies=[Depends(require_role("audit.delete"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Delete an audit event by ID with RBAC
    """
    try:
        with tracer.start_as_current_span("audit_delete"):
            service = AuditService(db)
            deleted = await service.delete_event(event_id, context["user"])
            if not deleted:
                raise NotFoundError(f"Audit event {event_id} not found")
        logger.info(f"Audit event {event_id} deleted by {context['user'].sub}")
    except NotFoundError as ne:
        logger.warning(str(ne))
        raise HTTPException(status_code=404, detail=str(ne))
    except ServiceUnavailableError:
        logger.error("Audit service unavailable during delete operation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit service is currently unavailable"
        )
