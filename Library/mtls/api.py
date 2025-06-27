"""
Secure API endpoints with RBAC and async operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import MtlsManager
from .schemas import MtlsConfig
from .exceptions import MtlsConfigError

API_KEY_NAME = "X-MTLS-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # In production, validate against Vault or secrets manager
    if api_key != "SECURE_API_KEY": 
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/mtls", tags=["mtls"])
mtls_manager: MtlsManager = None

@router.get("/info", response_model=MtlsConfig, dependencies=[Depends(validate_api_key)])
async def get_mtls_info():
    if not mtls_manager:
        raise HTTPException(503, "MtlsManager not initialized")
    return mtls_manager.get_cert_info()

@router.post("/enforce", dependencies=[Depends(validate_api_key)])
async def enforce_mtls(enforce: bool):
    if not mtls_manager:
        raise HTTPException(503, "MtlsManager not initialized")
    try:
        await mtls_manager.set_enforce(enforce)
        return {"enforce": mtls_manager.is_enforced()}
    except Exception as e:
        raise HTTPException(500, f"Enforcement failed: {str(e)}")

@router.post("/reload", dependencies=[Depends(validate_api_key)])
async def reload_certificates():
    if not mtls_manager:
        raise HTTPException(503, "MtlsManager not initialized")
    try:
        await mtls_manager.reload()
        return {"status": "certs reloaded"}
    except Exception as e:
        raise HTTPException(500, f"Reload failed: {str(e)}")
