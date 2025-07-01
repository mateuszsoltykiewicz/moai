from fastapi import APIRouter, Depends, Request, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import HomeKitBridgeManager
from .schemas import AccessoryListResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/homekit", tags=["homekit"])

@router.get("/accessories", response_model=AccessoryListResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "homekit", "read"))])
async def list_accessories():
    try:
        accessories = await HomeKitBridgeManager.list_accessories()
        return AccessoryListResponse(accessories=accessories)
    except Exception as e:
        logger.error(f"Failed to list accessories: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.post("/refresh", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "homekit", "write"))])
async def refresh_accessories(request: Request):
    try:
        await HomeKitBridgeManager.refresh_accessories()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to refresh accessories: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
