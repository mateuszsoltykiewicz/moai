from fastapi import APIRouter, Depends, Body, HTTPException, Request
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import StateServerManager
from .schemas import StateResponse, StateUpdateRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/state", tags=["state"])

@router.get("/{key}", response_model=StateResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "state", "read"))])
async def get_state(request: Request, key: str):
    try:
        value = await StateServerManager.get(key)
        return {"key": key, "value": value}
    except Exception as e:
        logger.warning(f"State get failed: {e}")
        raise HTTPException(404, str(e))

@router.put("/{key}", response_model=StateResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "state", "write"))])
async def set_state(request: Request, key: str, req: StateUpdateRequest = Body(...)):
    try:
        await StateServerManager.set(key, req.value)
        value = await StateServerManager.get(key)
        return {"key": key, "value": value}
    except Exception as e:
        logger.warning(f"State set failed: {e}")
        raise HTTPException(500, str(e))
