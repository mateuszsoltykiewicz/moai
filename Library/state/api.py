"""
API endpoints for StateManager.
"""

from fastapi import APIRouter, HTTPException, status, Body
from .manager import StateManager
from .schemas import StateResponse, StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError
from typing import Dict, Any

router = APIRouter(prefix="/state", tags=["state"])

state_manager = StateManager()

@router.get("/{key}", response_model=StateResponse)
async def get_state(key: str):
    """
    Get state for a key.
    """
    try:
        value = await state_manager.get(key)
        return {"key": key, "value": value}
    except StateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{key}", response_model=StateResponse)
async def set_state(key: str, req: StateUpdateRequest = Body(...)):
    """
    Set state for a key.
    """
    if req.updates is not None:
        try:
            await state_manager.update(key, req.updates)
        except StateValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except StateNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        await state_manager.set(key, req.value)
    value = await state_manager.get(key)
    return {"key": key, "value": value}

@router.delete("/{key}", status_code=204)
async def delete_state(key: str):
    """
    Delete state for a key.
    """
    try:
        await state_manager.delete(key)
    except StateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=Dict[str, Any])
async def get_all_state():
    """
    Get all state.
    """
    return await state_manager.get_all()
