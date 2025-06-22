"""
App State API Router

- Configurable RBAC (via config and dependency)
- Pre/post custom hooks
- Default executions
- Comprehensive metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
from schemas.state import AppStateResponse, AppStateUpdateRequest
from api.dependencies import base_endpoint_processor, require_role
from core.state import AppState
from metrics.core import record_appstate_operation
from core.tracing import AsyncTracer
from core.logging import logger
import time

# Instantiate tracer globally or import a singleton if you have one
tracer = AsyncTracer("applib-appstate").get_tracer()

router = APIRouter(
    prefix="/appstate",
    tags=["appstate"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"}
    }
)

@router.get(
    "",
    response_model=AppStateResponse,
    summary="Get application state",
    description="Returns the current operational state of the application.",
)
async def get_app_state(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="appstate:get",
            pre_hook="api.hooks.appstate.before_get",
            post_hook="api.hooks.appstate.after_get",
            dependencies=[Depends(require_role("appstate.read"))]
        )
    )
):
    """
    Get current application state with:
    - RBAC
    - Pre/post hooks
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("get_app_state"):
        state = await AppState().get_state()
        response = AppStateResponse(**state.dict())
    duration = time.monotonic() - start_time
    record_appstate_operation("get", duration)
    logger.info(f"App state fetched by {context['user'].sub} in {duration:.3f}s")
    return response

@router.patch(
    "",
    response_model=AppStateResponse,
    summary="Update application state",
    description="Update the application's operational state (e.g., to maintenance or paused)."
)
async def update_app_state(
    update: AppStateUpdateRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="appstate:update",
            pre_hook="api.hooks.appstate.before_update",
            post_hook="api.hooks.appstate.after_update",
            dependencies=[Depends(require_role("appstate.update"))]
        )
    )
):
    """
    Update application state with:
    - RBAC
    - Pre/post hooks
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("update_app_state"):
        # Pre-hook validation result
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        await AppState().update_state(update.dict(exclude_unset=True), persist=True)
        state = await AppState().get_state()
        response = AppStateResponse(**state.dict())
    duration = time.monotonic() - start_time
    record_appstate_operation("update", duration)
    logger.info(f"App state updated by {context['user'].sub} in {duration:.3f}s")
    return response
