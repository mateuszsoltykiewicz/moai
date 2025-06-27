"""
API endpoints for UtilsManager (diagnostics).
"""

from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from .schemas import StatusResponse

API_KEY_NAME = "X-UTILS-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # In production, validate against Vault or a secrets manager
    if not api_key or api_key != "SECURE_API_KEY":
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/status", response_model=StatusResponse, dependencies=[Depends(validate_api_key)])
async def get_status():
    """
    Get status of the UtilsManager.
    """
    return StatusResponse(status="ok", message="UtilsManager is running.")
