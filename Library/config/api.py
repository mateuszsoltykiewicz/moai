"""
API endpoints for ConfigManager.

- Exposes /config/status and /config/update endpoints
"""

from fastapi import APIRouter, HTTPException, status, Body
from .manager import ConfigManager
from .schemas import AppConfig
from .exceptions import ConfigValidationError

router = APIRouter(prefix="/config", tags=["config"])

config_manager: ConfigManager = None  # Will be initialized at app startup

@router.get("/status", response_model=AppConfig)
async def get_config_status():
    """
    Get the current application configuration.
    """
    if config_manager is None:
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    return await config_manager.get()

@router.post("/update", response_model=AppConfig)
async def update_config(new_config: AppConfig = Body(...)):
    """
    Update the application configuration.
    """
    if config_manager is None:
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    try:
        await config_manager.set(new_config)
        return await config_manager.get()
    except ConfigValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
