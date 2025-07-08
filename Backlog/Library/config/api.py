from fastapi import APIRouter, HTTPException, Body, Depends
from .manager import ConfigManager
from .schemas import AppConfig
from .exceptions import ConfigValidationError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/config", tags=["config"])
config_manager: ConfigManager = None  # Initialized at app startup

@router.get("/status", response_model=AppConfig, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "config", "read"))])
async def get_config_status():
    if config_manager is None:
        logger.error("ConfigManager not initialized")
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    return await config_manager.get()

@router.post("/update", response_model=AppConfig, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "config", "write"))])
async def update_config(new_config: AppConfig = Body(...)):
    if config_manager is None:
        logger.error("ConfigManager not initialized")
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    try:
        await config_manager.set(new_config)
        logger.info("Config update requested")
        return await config_manager.get()
    except ConfigValidationError as e:
        logger.error(f"Config validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))
