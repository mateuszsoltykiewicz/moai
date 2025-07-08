"""
API endpoints for CoreManager.

- Exposes /core/status endpoint for health/status
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from .manager import CoreManager
from .schemas import CoreStatusResponse
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/core", tags=["core"])

# Assume core_manager is instantiated elsewhere and injected here
core_manager: CoreManager = CoreManager()

@router.get(
    "/status",
    response_model=CoreStatusResponse,
    dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "core", "read"))]
)
async def get_core_status():
    """
    Get the current status of the CoreManager.
    """
    try:
        return core_manager.get_status()
    except Exception as e:
        logger.error(f"Failed to get core status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
