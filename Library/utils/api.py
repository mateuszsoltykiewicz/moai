"""
API endpoints for UtilsManager (diagnostics).
"""

from fastapi import APIRouter
from .schemas import StatusResponse

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get status of the UtilsManager.
    """
    return StatusResponse(status="ok", message="UtilsManager is running.")
