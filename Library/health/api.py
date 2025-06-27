"""
API endpoints with security and caching.
"""

from fastapi import APIRouter, Response, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import HealthManager
from .schemas import HealthCheckResponse

API_KEY_NAME = "X-HEALTH-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_health_key(api_key: str = Security(api_key_scheme)):
    # Replace with real validation (e.g., Vault lookup)
    if api_key != "SECURE_API_KEY":
        raise HTTPException(403, "Invalid health API key")

router = APIRouter(prefix="/health", tags=["health"])

# Initialize with app version and timeout
health_manager = HealthManager(version="1.0.0", timeout=3.0)

@router.get("/livez", include_in_schema=False)
async def liveness():
    """Minimal liveness probe (no dependencies)"""
    return Response(content="alive", media_type="text/plain")

@router.get("/readyz", response_model=HealthCheckResponse, dependencies=[Depends(validate_health_key)])
async def readiness():
    """Comprehensive readiness check with timeout protection"""
    return await health_manager.get_health_status()
