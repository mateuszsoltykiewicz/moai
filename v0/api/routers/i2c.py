"""
I2C API Router

- Configurable RBAC (via require_role)
- Pre/post custom hooks for validation/audit
- Default executions
- Comprehensive metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from typing import Dict, Any
from schemas.i2c import (
    I2CCommandConfigRequest,
    I2CCommandQueueRequest,
    I2CCommandResponse
)
from ..dependencies.base import base_endpoint_processor
from ..dependencies.security import require_role
from metrics.i2c import record_i2c_operation
from core.tracing import AsyncTracer
from core.logging import logger
from adapters.i2c import I2CAdapter
import time

tracer = AsyncTracer("applib-i2c").get_tracer()

router = APIRouter(
    prefix="/i2c",
    tags=["i2c"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"}
    }
)

# In-memory adapter registry (replace with DI/persistent store in production)
I2C_ADAPTERS: Dict[str, I2CAdapter] = {}

def get_adapter(adapter_id: str) -> I2CAdapter:
    if adapter_id not in I2C_ADAPTERS:
        I2C_ADAPTERS[adapter_id] = I2CAdapter(adapter_id)
    return I2C_ADAPTERS[adapter_id]

@router.post(
    "/start/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="Start I2C adapter"
)
async def start_adapter(
    adapter_id: str,
    req: I2CCommandConfigRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="i2c:start",
            pre_hook="api.hooks.i2c.before_start",
            post_hook="api.hooks.i2c.after_start",
            dependencies=[Depends(require_role("i2c.start"))]
        )
    )
):
    """
    Start/configure an I2C adapter.
    - RBAC via 'i2c.start'
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
        with tracer.start_as_current_span("i2c_start"):
            adapter = get_adapter(adapter_id)
            await adapter.configure(
                frequency=req.frequency,
                address=req.address,
                options=req.options
            )
            response = I2CCommandResponse(
                adapter_id=adapter_id,
                success=True,
                message="I2C adapter started"
            )
        duration = time.monotonic() - start_time
        record_i2c_operation("start", duration)
        logger.info(f"I2C adapter {adapter_id} started in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"I2C start failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start I2C adapter: {str(e)}"
        )

@router.post(
    "/queue/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="Queue I2C commands"
)
async def queue_i2c_commands(
    adapter_id: str,
    req: I2CCommandQueueRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="i2c:queue",
            pre_hook="api.hooks.i2c.before_queue",
            post_hook="api.hooks.i2c.after_queue",
            dependencies=[Depends(require_role("i2c.queue"))]
        )
    )
):
    """
    Queue commands for an I2C adapter.
    - RBAC via 'i2c.queue'
    - Pre/post hooks for validation/audit
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        with tracer.start_as_current_span("i2c_queue"):
            adapter = get_adapter(adapter_id)
            results = await adapter.queue_commands(req.commands)
            response = I2CCommandResponse(
                adapter_id=adapter_id,
                success=True,
                message="Commands queued",
                data=results
            )
        duration = time.monotonic() - start_time
        record_i2c_operation("queue", duration)
        logger.info(f"Queued {len(req.commands)} commands for I2C adapter {adapter_id} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"I2C queue failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue I2C commands: {str(e)}"
        )

@router.get(
    "/status/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="Get I2C adapter status"
)
async def get_i2c_status(
    adapter_id: str,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="i2c:status",
            dependencies=[Depends(require_role("i2c.read"))]
        )
    )
):
    """
    Get the current status of an I2C adapter.
    - RBAC via 'i2c.read'
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("i2c_status"):
            adapter = get_adapter(adapter_id)
            status = await adapter.get_status()
            response = I2CCommandResponse(
                adapter_id=adapter_id,
                success=True,
                message="I2C adapter status fetched",
                data=status
            )
        duration = time.monotonic() - start_time
        record_i2c_operation("status", duration)
        logger.info(f"Fetched status for I2C adapter {adapter_id} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"I2C status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get I2C adapter status: {str(e)}"
        )
