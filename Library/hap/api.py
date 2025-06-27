from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from .manager import HAPManager
from .schemas import HAPStatusResponse

API_KEY_NAME = "X-HAP-Key"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_hap_key(api_key: str = Security(api_key_scheme)):
    # Replace with real validation (e.g., Vault lookup)
    if api_key != "SECURE_API_KEY":
        raise HTTPException(403, "Invalid HAP API key")

router = APIRouter(prefix="/hap", tags=["hap"])
hap_manager: HAPManager = None

@router.get("/status", response_model=HAPStatusResponse, dependencies=[Depends(validate_hap_key)])
async def get_hap_status():
    if not hap_manager:
        raise HTTPException(503, "HAPManager not initialized")
    return await hap_manager.get_status()
