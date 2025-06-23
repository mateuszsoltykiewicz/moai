"""
API endpoints for HAPManager.

- Exposes /hap/status for diagnostics
"""

from fastapi import APIRouter, HTTPException
from .manager import HAPManager
from .schemas import HAPStatusResponse

router = APIRouter(prefix="/hap", tags=["hap"])

hap_manager: HAPManager = None  # Should be initialized at app startup

@router.get("/status", response_model=HAPStatusResponse)
async def get_hap_status():
    """
    Get current HAP bridge status.
    """
    if not hap_manager:
        raise HTTPException(status_code=503, detail="HAPManager not initialized")
    return await hap_manager.get_status()
