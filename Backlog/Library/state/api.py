from fastapi import APIRouter, HTTPException, Body, Depends, Request
from .manager import StateManager
from .schemas import StateResponse, StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/state", tags=["state"])
state_manager: StateManager = None

@router.get("/{key}", response_model=StateResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "state", "read"))])
async def get_state(request: Request, key: str):
    try:
        value = await state_manager.get(key)
        return {"key": key, "value": value}
    except StateNotFoundError as e:
        logger.warning(f"State not found: {key}")
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"State get failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.put("/{key}", response_model=StateResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "state", "write"))])
async def set_state(request: Request, key: str, req: StateUpdateRequest = Body(...)):
    try:
        if req.updates is not None:
            await state_manager.update(key, req.updates)
        else:
            await state_manager.set(key, req.value)
        value = await state_manager.get(key)
        return {"key": key, "value": value}
    except StateValidationError as e:
        logger.warning(f"State validation failed: {key} - {e}")
        raise HTTPException(422, str(e))
    except StateNotFoundError as e:
        logger.warning(f"State not found: {key}")
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"State set failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
