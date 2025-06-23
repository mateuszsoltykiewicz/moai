"""
API endpoints for HealthManager.

- Exposes /health/livez for liveness probe
- Exposes /health/readyz for readiness probe
"""

from fastapi import APIRouter, Response
from .manager import HealthManager
from .schemas import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["health"])

health_manager = HealthManager()

@router.get("/livez", include_in_schema=False)
async def liveness():
    """
    Liveness probe.
    """
    return Response(content="alive", media_type="text/plain")

@router.get("/readyz", response_model=HealthCheckResponse)
async def readiness():
    """
    Readiness probe.
    """
    return await health_manager.get_health_status()
