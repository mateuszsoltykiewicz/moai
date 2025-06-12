from fastapi import Request
from subservices.adapters.i2c import I2CAdapter
import asyncio

"""
Health API Router

- /livez: Liveness probe (is the process up)
- /readyz: Readiness probe (are dependencies healthy)
- /metrics: Prometheus metrics endpoint (added via instrumentator in main.py)
- Extensible subsystem checks (DB, Kafka, adapters, etc.)
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from AppLib.models.schemas import HealthCheckSchema
import time
import platform

router = APIRouter(tags=["health"])

APP_START_TIME = time.time()

async def check_database(request: Request) -> str:
    try:
        db_session_factory = getattr(request.app.state, "db_session_factory", None)
        if db_session_factory:
            async with db_session_factory() as session:
                await session.execute("SELECT 1")
            return "ok"
        return "skipped"
    except Exception:
        return "fail"

async def check_kafka(request: Request) -> str:
    try:
        kafka_producer = getattr(request.app.state, "kafka_producer", None)
        if kafka_producer:
            # Optionally send a metadata request or similar
            return "ok"
        return "skipped"
    except Exception:
        return "fail"

async def check_adapters(request: Request) -> str:
    try:
        adapters = getattr(request.app.state, "adapters", {})
        if adapters:
            # Optionally run ping/status on each adapter
            return "ok"
        return "skipped"
    except Exception:
        return "fail"
    
async def check_i2c(request: Request) -> str:
    """Check health of all I2C adapters"""
    try:
        if not hasattr(request.app.state, "i2c_adapters"):
            return "skipped"
        
        adapters: Dict[str, I2CAdapter] = request.app.state.i2c_adapters
        if not adapters:
            return "skipped"

        health_statuses = await asyncio.gather(
            *(adapter.health_check() for adapter in adapters.values())
        )
        return "ok" if all(health_statuses) else "fail"
    except Exception:
        return "fail"

async def check_mtls(request: Request) -> str:
    """Check if client certificate info is present (proxy must pass headers)"""
    cert_info = request.headers.get("x-client-cert")
    return "ok" if cert_info else "fail"

@router.get(
    "/livez",
    summary="Liveness probe",
    description="Returns 200 if the process is running (for orchestrators/liveness probes)."
)
async def liveness():
    """Liveness probe: is the process up? No dependencies checked."""
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "alive"})

@router.get(
    "/readyz",
    response_model=HealthCheckSchema,
    summary="Readiness probe"
)
async def readiness(request: Request):
    uptime = int(time.time() - APP_START_TIME)
    version = getattr(request.app, "version", platform.python_version())
    
    checks = {
        "database": await check_database(request),
        "kafka": await check_kafka(request),
        "i2c": await check_i2c(request),
        "mtls": await check_mtls(request),
    }
    
    status_val = "ok" if all(v in ("ok", "skipped") for v in checks.values()) else "degraded"
    if any(v == "fail" for v in checks.values()):
        status_val = "fail"
    
    return HealthCheckSchema(
        status=status_val,
        uptime_seconds=uptime,
        version=version,
        checks=checks
    )