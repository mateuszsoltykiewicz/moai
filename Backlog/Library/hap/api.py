from fastapi import APIRouter, HTTPException, Depends, Request
from .manager import HAPManager
from .schemas import HAPStatusResponse
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/hap", tags=["hap"])
hap_manager: HAPManager = None

@router.get("/status", response_model=HAPStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "hap", "read"))])
async def get_hap_status():
    if not hap_manager:
        logger.error("HAPManager not initialized")
        raise HTTPException(503, "HAPManager not initialized")
    return await hap_manager.get_status()
