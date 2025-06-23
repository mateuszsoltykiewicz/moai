"""
Production-ready alarms management with:
- RBAC based on configuration
- Custom hooks for alarm validation and auditing
- Comprehensive metrics and telemetry
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
from uuid import UUID
from core.config import get_config
from core.metrics import record_alarm_operation
from core.telemetry import tracer
from models.schemas.alarms import AlarmCreate, AlarmResponse, AlarmUpdate
from api.dependencies import base_endpoint_processor, require_role
from services.alarms import AlarmService
import time

router = APIRouter(
    prefix="/alarms",
    tags=["alarms"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"}
    }
)

@router.post(
    "",
    response_model=AlarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alarm"
)
async def create_alarm(
    alarm_ AlarmCreate = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="alarms:create",
            pre_hook="api.hooks.alarms.validate_alarm_creation",
            post_hook="api.hooks.alarms.audit_alarm_creation",
            dependencies=[Depends(require_role("alarms.create"))]
        )
    )
):
    """
    Create a new alarm with:
    - RBAC based on 'alarms.create' permission
    - Custom validation hook
    - Audit logging hook
    """
    start_time = time.monotonic()
    
    # Execute custom validation from pre-hook
    if "validation_result" in context:
        if not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
    
    # Create alarm
    with tracer.start_as_current_span("create_alarm"):
        service = AlarmService()
        alarm = await service.create(alarm_data, context["user"])
    
    # Record metrics
    duration = time.monotonic() - start_time
    record_alarm_operation("create", duration)
    
    return alarm

@router.get(
    "",
    response_model=List[AlarmResponse],
    summary="List alarms"
)
async def list_alarms(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="alarms:list",
            dependencies=[Depends(require_role("alarms.read"))]
        )
    )
):
    """List alarms with RBAC and telemetry"""
    start_time = time.monotonic()
    
    with tracer.start_as_current_span("list_alarms"):
        service = AlarmService()
        alarms = await service.list(context["user"])
    
    duration = time.monotonic() - start_time
    record_alarm_operation("list", duration, count=len(alarms))
    
    return alarms

@router.patch(
    "/{alarm_id}",
    response_model=AlarmResponse,
    summary="Update an alarm"
)
async def update_alarm(
    alarm_id: UUID,
    update_ AlarmUpdate = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="alarms:update",
            pre_hook="api.hooks.alarms.validate_alarm_update",
            post_hook="api.hooks.alarms.audit_alarm_update",
            dependencies=[Depends(require_role("alarms.update"))]
        )
    )
):
    """Update an alarm with validation and auditing"""
    start_time = time.monotonic()
    
    # Execute custom validation
    if "validation_result" in context:
        if not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
    
    # Update alarm
    with tracer.start_as_current_span("update_alarm"):
        service = AlarmService()
        alarm = await service.update(alarm_id, update_data, context["user"])
    
    # Record metrics
    duration = time.monotonic() - start_time
    record_alarm_operation("update", duration)
    
    return alarm
