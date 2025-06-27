from fastapi import APIRouter, HTTPException, Body, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import StateManager
from .schemas import StateResponse, StateUpdateRequest
from .exceptions import StateValidationError, StateNotFoundError

API_KEY_NAME = "X-STATE-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # Validate against Vault or secrets manager
    if not api_key or api_key != "SECURE_API_KEY": 
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/state", tags=["state"])
state_manager: StateManager = None

@router.get("/{key}", response_model=StateResponse, dependencies=[Depends(validate_api_key)])
async def get_state(key: str):
    try:
        value = await state_manager.get(key)
        return {"key": key, "value": value}
    except StateNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")

@router.put("/{key}", response_model=StateResponse, dependencies=[Depends(validate_api_key)])
async def set_state(key: str, req: StateUpdateRequest = Body(...)):
    try:
        if req.updates is not None:
            await state_manager.update(key, req.updates)
        else:
            await state_manager.set(key, req.value)
        value = await state_manager.get(key)
        return {"key": key, "value": value}
    except StateValidationError as e:
        raise HTTPException(422, str(e))
    except StateNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")
