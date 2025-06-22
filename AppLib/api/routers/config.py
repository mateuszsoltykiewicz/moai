"""
Configuration API Router

- Secure retrieval and update of application configuration
- Integrates with async config subservice
- Configurable RBAC
- Pre/post hooks
- Metrics and telemetry
- Structured logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
from core.config import AsyncConfigManager, get_config
from models.schemas.config import ConfigResponseSchema, ConfigUpdateRequest
from api.dependencies import base_endpoint_processor, require_role
from core.metrics import record_config_operation
from core.tracing import AsyncTracer
from core.logging import logger
import time

# Instantiate tracer globally or import a singleton if you have one
tracer = AsyncTracer("applib-config").get_tracer()

router = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"}
    }
)

@router.get(
    "",
    response_model=ConfigResponseSchema,
    summary="Get current configuration",
    description="Retrieve the current application configuration."
)
async def get_configuration(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="config:get",
            pre_hook="api.hooks.config.before_get",
            post_hook="api.hooks.config.after_get",
            dependencies=[Depends(require_role("config.read"))]
        )
    )
):
    """
    Get current configuration with:
    - RBAC
    - Pre/post hooks
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("get_configuration"):
        config_mgr = AsyncConfigManager("configs/app_config.json")
        await config_mgr.start()
        config = await config_mgr.get()
        response = ConfigResponseSchema(config=config.model_dump())
    duration = time.monotonic() - start_time
    record_config_operation("get", duration)
    logger.info(f"Configuration fetched in {duration:.3f}s")
    return response

@router.patch(
    "",
    response_model=ConfigResponseSchema,
    summary="Update configuration",
    description="Update the application configuration. Triggers hot reload."
)
async def update_configuration(
    update: ConfigUpdateRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="config:update",
            pre_hook="api.hooks.config.before_update",
            post_hook="api.hooks.config.after_update",
            dependencies=[Depends(require_role("config.update"))]
        )
    )
):
    """
    Update configuration with:
    - RBAC
    - Pre/post hooks
    - Validation
    - Metrics and tracing
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("update_configuration"):
        # Pre-hook validation result
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        config_mgr = AsyncConfigManager("configs/app_config.json")
        await config_mgr.start()
        # Validate and apply new config
        try:
            new_config = await config_mgr.schema.model_validate_async(update.config)
            await config_mgr.set(new_config)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        response = ConfigResponseSchema(config=new_config.model_dump())
    duration = time.monotonic() - start_time
    record_config_operation("update", duration)
    logger.info(f"Configuration updated in {duration:.3f}s")
    return response
