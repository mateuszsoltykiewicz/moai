"""
Custom hooks for appstate router
"""

from fastapi import Request
from schemas.state import AppStateUpdateRequest
from core.logging import logger

async def before_get(request: Request):
    # Example: Log access or check custom header
    logger.info("Pre-hook: before_get called")
    return {}

async def after_get(request: Request, response, context):
    # Example: Audit log or custom metric
    logger.info("Post-hook: after_get called")
    return {}

async def before_update(request: Request, update: AppStateUpdateRequest):
    # Example: Validate status transition
    allowed = {"running", "paused", "maintenance"}
    if update.status not in allowed:
        return {"validation_result": {"valid": False, "message": f"Invalid state: {update.status}"}}
    logger.info(f"Pre-hook: before_update called with status={update.status}")
    return {"validation_result": {"valid": True}}

async def after_update(request: Request, response, context):
    # Example: Audit log or notification
    logger.info("Post-hook: after_update called")
    return {}
