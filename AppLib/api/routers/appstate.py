"""
App State API Router

- Allows querying and updating the application's operational state.
- Useful for orchestrators, health dashboards, and admin tools.
- All endpoints are async, schema-driven, and secured.
"""

from fastapi import APIRouter, Depends, status, Request
from models.schemas import AppStateSchema, AppStateUpdateRequest
from api.dependencies import get_current_user
from api.main import APIException

import time

router = APIRouter(tags=["appstate"])

# In-memory state (replace with persistent store or service in production)
APP_STATE = {
    "status": "running",
    "version": "1.0.0",
    "start_time": time.time(),
    "details": {}
}

@router.get(
    "/",
    response_model=AppStateSchema,
    summary="Get application state",
    description="Returns the current operational state of the application."
)
async def get_app_state(
    user=Depends(get_current_user)
):
    """
    Retrieve the current application state, including status, version, and uptime.
    """
    uptime = int(time.time() - APP_STATE["start_time"])
    return AppStateSchema(
        status=APP_STATE["status"],
        uptime_seconds=uptime,
        version=APP_STATE["version"],
        details=APP_STATE["details"]
    )

@router.post(
    "/",
    response_model=AppStateSchema,
    summary="Update application state",
    description="Update the application's operational state (e.g., to maintenance or paused)."
)
async def update_app_state(
    req: AppStateUpdateRequest,
    user=Depends(get_current_user)
):
    """
    Update the application state (e.g., to maintenance or paused).
    """
    # In production, validate permissions and propagate state change to subsystems
    valid_states = {"running", "paused", "maintenance"}
    if req.status not in valid_states:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Invalid state: {req.status}",
            details={"allowed_states": list(valid_states)}
        )
    APP_STATE["status"] = req.status
    if req.reason:
        APP_STATE["details"]["last_reason"] = req.reason
    return await get_app_state(user)
