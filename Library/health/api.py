"""
API endpoints with security and caching.
"""

from fastapi import APIRouter, Response, Depends
from .manager import HealthManager
from .schemas import HealthCheckResponse
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Initialize with app version and timeout
health_manager = HealthManager(version="1.0.0", timeout=3.0)

@router.get("/livez", include_in_schema=False)
async def liveness():
    """Minimal liveness probe (no dependencies)"""
    return Response(content="alive", media_type="text/plain")

@router.get("/readyz", response_model=HealthCheckResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "health", "read"))])
async def readiness():
    """Comprehensive readiness check with timeout protection"""
    return await health_manager.get_health_status()
