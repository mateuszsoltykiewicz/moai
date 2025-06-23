"""
CANBus API Router

- Configurable RBAC (via require_role)
- Pre/post custom hooks for validation/audit
- Default executions
- Comprehensive metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from typing import Dict, Any, List
from uuid import UUID
from schemas.canbus import (
    CANBusStreamConfigRequest,
    CANBusStreamConfigResponse,
    CANBusStatusResponse,
    CANBusMessage
)
from dependencies.base import base_endpoint_processor
from dependencies.security import require_role
from metrics.metrics import record_canbus_operation
from core.tracing import AsyncTracer
from core.logging import logger
from adapters.canbus import CANBusAdapter
import time

tracer = AsyncTracer("applib-canbus").get_tracer()

router = APIRouter(
    prefix="/canbus",
    tags=["canbus"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"}
    }
)

# In-memory adapter registry (replace with persistent store/DI in production)
CANBUS_ADAPTERS: Dict[str, CANBusAdapter] = {}

@router.post(
    "/stream/configure",
    response_model=CANBusStreamConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Configure CANBus streaming"
)
async def configure_canbus_stream(
    config: CANBusStreamConfigRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="canbus:configure_stream",
            pre_hook="api.hooks.canbus.before_configure",
            post_hook="api.hooks.canbus.after_configure",
            dependencies=[Depends(require_role("canbus.configure"))]
        )
    )
):
    """
    Configure a CANBus adapter for data streaming.
    - RBAC via 'canbus.configure'
    - Pre/post hooks for validation/audit
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        # Pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        with tracer.start_as_current_span("canbus_configure_stream"):
            adapter = CANBusAdapter(channel=config.adapter_id, bitrate=config.bitrate)
            await adapter.configure(filters=config.filters)
            CANBUS_ADAPTERS[config.adapter_id] = adapter
            response = CANBusStreamConfigResponse(success=True, message="CANBus stream configured.")
        duration = time.monotonic() - start_time
        record_canbus_operation("configure", duration)
        logger.info(f"CANBus stream configured for adapter {config.adapter_id} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"CANBus configuration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure CANBus stream: {str(e)}"
        )

@router.get(
    "/status/{adapter_id}",
    response_model=CANBusStatusResponse,
    summary="Get CANBus adapter status"
)
async def get_canbus_status(
    adapter_id: str,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="canbus:get_status",
            dependencies=[Depends(require_role("canbus.read"))]
        )
    )
):
    """
    Get the current status of a CANBus adapter.
    - RBAC via 'canbus.read'
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("canbus_get_status"):
        adapter = CANBUS_ADAPTERS.get(adapter_id)
        if not adapter:
            logger.warning(f"CANBus adapter '{adapter_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CANBus adapter '{adapter_id}' not found"
            )
        status = "streaming" if getattr(adapter, "_streaming", False) else "stopped"
        response = CANBusStatusResponse(
            adapter_id=adapter_id,
            status=status,
            last_configured=getattr(adapter, "last_configured", None)
        )
    duration = time.monotonic() - start_time
    record_canbus_operation("get_status", duration)
    logger.info(f"Status for CANBus adapter {adapter_id} fetched in {duration:.3f}s")
    return response

@router.get(
    "/stream/{adapter_id}",
    response_model=List[CANBusMessage],
    summary="Stream CANBus messages"
)
async def stream_canbus_messages(
    adapter_id: str,
    max_messages: int = 100,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="canbus:stream_messages",
            dependencies=[Depends(require_role("canbus.read"))]
        )
    )
):
    """
    Stream CANBus messages from the adapter.
    - RBAC via 'canbus.read'
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("canbus_stream_messages"):
        adapter = CANBUS_ADAPTERS.get(adapter_id)
        if not adapter or not getattr(adapter, "_streaming", False):
            logger.warning(f"CANBus adapter '{adapter_id}' not streaming or not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CANBus adapter '{adapter_id}' not streaming."
            )
        messages = []
        async for msg in adapter.read_stream(max_messages=max_messages):
            messages.append(msg)
    duration = time.monotonic() - start_time
    record_canbus_operation("stream", duration, count=len(messages))
    logger.info(f"Streamed {len(messages)} CANBus messages from {adapter_id} in {duration:.3f}s")
    return messages
