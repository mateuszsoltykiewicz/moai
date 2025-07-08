from fastapi import APIRouter, Depends, Request, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import DisasterDetectorManager
from .schemas import DisasterStatusResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/disaster", tags=["disaster"])

@router.get("/status", response_model=DisasterStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "disaster", "read"))])
async def get_disaster_status():
    try:
        status = await DisasterDetectorManager.get_disaster_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get disaster status: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
