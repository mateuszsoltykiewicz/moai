"""
Health API Router

- Liveness and readiness probes
- Optional RBAC for readiness
- Pre/post hooks for extensibility
- Metrics and tracing
- Structured logging
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from schemas.health import HealthCheckResponse, HealthCheckDetail
from metrics.health import record_health_check
from core.tracing import AsyncTracer
from core.logging import logger
from api.dependencies import base_endpoint_processor, require_role
from utils.health import health_registry
import time
import platform

tracer = AsyncTracer("applib-health").get_tracer()
APP_START_TIME = time.time()
APP_VERSION = "1.2.3"  # Should be set from config or env

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={503: {"description": "Service Unavailable"}}
)

@router.get("/livez", include_in_schema=False)
async def liveness():
    """Liveness probe - always returns 200 when service is running"""
    return JSONResponse(content={"status": "alive"}, status_code=200)

@router.get(
    "/readyz",
    response_model=HealthCheckResponse,
    summary="Readiness probe"
)
async def readiness(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="health:readyz",
            pre_hook="api.hooks.health.before_readyz",
            post_hook="api.hooks.health.after_readyz",
            # Uncomment below to require RBAC for readiness (optional)
            # dependencies=[Depends(require_role("health.read"))]
        )
    ),
    request: Request = None
):
    """
    Readiness probe with:
    - Default and custom system checks
    - Pre/post hook integration
    - Metrics and tracing
    - Structured logging
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("readiness_probe"):
        checks: Dict[str, HealthCheckDetail] = {}

        # --- Default checks ---
        # Register these at app startup or here as needed
        if not health_registry.get_checks():
            from api.routers.health import check_database, check_redis
            health_registry.register("database", check_database)
            health_registry.register("redis", check_redis)

        for name, func in health_registry.get_checks().items():
            try:
                result = await func()
                checks[name] = HealthCheckDetail(**result)
            except Exception as e:
                checks[name] = HealthCheckDetail(status="fail", details={"error": str(e)})

        # --- Custom checks from pre-hook ---
        if "custom_checks" in context:
            for name, result in context["custom_checks"].items():
                checks[name] = HealthCheckDetail(**result)

        # Determine overall status
        overall_status = "ok" if all(c.status == "ok" for c in checks.values()) else "degraded"

        duration = time.monotonic() - start_time
        record_health_check("readyz", overall_status, duration)
        logger.info(f"Readiness probe result: {overall_status} ({duration:.3f}s)")

        uptime = int(time.time() - APP_START_TIME)
        return HealthCheckResponse(
            status=overall_status,
            checks=checks,
            uptime_seconds=uptime,
            version=APP_VERSION
        )

# --- Default health check implementations ---

async def check_database() -> Dict[str, Any]:
    """Default database health check"""
    try:
        # Replace with your actual DB adapter check
        # Example: await db.execute("SELECT 1")
        return {"status": "ok", "details": {"info": "DB connected"}}
    except Exception as e:
        return {"status": "fail", "details": {"error": str(e)}}

async def check_redis() -> Dict[str, Any]:
    """Default Redis health check"""
    try:
        # Replace with your actual Redis adapter check
        # Example: await redis.ping()
        return {"status": "ok", "details": {"info": "Redis ping ok"}}
    except Exception as e:
        return {"status": "fail", "details": {"error": str(e)}}
