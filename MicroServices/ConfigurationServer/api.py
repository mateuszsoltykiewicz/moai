from fastapi import APIRouter, Depends, Request, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import ConfigServerManager
from .schemas import ConfigQueryRequest, ConfigResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/config", tags=["config"])

@router.get("/{service}", response_model=ConfigResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "config", "read"))])
async def get_config(request: Request, service: str, version: str = "latest"):
    """
    Retrieve configuration for a service
    """
    try:
        config = await ConfigServerManager.get_config(service, version)
        return ConfigResponse(service=service, version=version, config=config)
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.post("/hot-reload", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "config", "write"))])
async def hot_reload(request: Request, req: ConfigQueryRequest):
    """
    Trigger hot-reload for a service's configuration
    """
    try:
        await ConfigServerManager.reload_config(req.service)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Config reload failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
