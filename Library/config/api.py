from fastapi import APIRouter, HTTPException, status, Body, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import ConfigManager
from .schemas import AppConfig
from .exceptions import ConfigValidationError
from .utils import log_info

API_KEY_NAME = "X-CONFIG-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_config_api_key(api_key: str = Security(api_key_scheme)):
    if api_key != "VALID_API_KEY":  # Replace with real validation
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/config", tags=["config"])
config_manager: ConfigManager = None  # Will be initialized at app startup

@router.get("/status", response_model=AppConfig, dependencies=[Depends(validate_config_api_key)])
async def get_config_status():
    if config_manager is None:
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    return await config_manager.get()

@router.post("/update", response_model=AppConfig, dependencies=[Depends(validate_config_api_key)])
async def update_config(new_config: AppConfig = Body(...)):
    if config_manager is None:
        raise HTTPException(status_code=503, detail="ConfigManager not initialized")
    try:
        await config_manager.set(new_config)
        log_info("Config update requested")
        return await config_manager.get()
    except ConfigValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
