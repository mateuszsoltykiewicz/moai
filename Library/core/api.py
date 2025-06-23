"""
API endpoints for CoreManager.

- Exposes /core/status endpoint for health/status
"""

from fastapi import APIRouter
from .manager import CoreManager
from .schemas import CoreStatusResponse

router = APIRouter(prefix="/core", tags=["core"])

# Assume core_manager is instantiated elsewhere and injected here
core_manager: CoreManager = CoreManager()

@router.get("/status", response_model=CoreStatusResponse)
async def get_core_status():
    """
    Get the current status of the CoreManager.
    """
    return core_manager.get_status()
