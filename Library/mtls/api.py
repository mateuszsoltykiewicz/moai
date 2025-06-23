"""
API endpoints for MtlsManager.

- Exposes /mtls/info for diagnostics
- Optionally exposes /mtls/enforce to toggle enforcement (if allowed)
"""

from fastapi import APIRouter, HTTPException
from .manager import MtlsManager
from .schemas import MtlsConfig

router = APIRouter(prefix="/mtls", tags=["mtls"])

mtls_manager: MtlsManager = None  # Should be initialized at app startup

@router.get("/info", response_model=MtlsConfig)
async def get_mtls_info():
    """
    Get current mTLS configuration and cert info.
    """
    if not mtls_manager:
        raise HTTPException(status_code=503, detail="MtlsManager not initialized")
    return mtls_manager._config

@router.post("/enforce")
async def enforce_mtls(enforce: bool):
    """
    (Optional) Dynamically enforce or relax mTLS (if allowed by policy).
    """
    if not mtls_manager:
        raise HTTPException(status_code=503, detail="MtlsManager not initialized")
    mtls_manager._config.enforce = enforce
    mtls_manager.setup()
    return {"enforce": mtls_manager.is_enforced()}
