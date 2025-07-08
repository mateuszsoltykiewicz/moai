from fastapi import APIRouter, HTTPException, Query, Depends, Request
from .manager import TracingManager
from .schemas import TraceQueryResponse
from .exceptions import TraceNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tracing", tags=["tracing"])
tracing_manager: TracingManager = None

@router.get("/status", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "tracing", "read"))])
async def tracing_status():
    if not tracing_manager:
        logger.error("TracingManager not initialized")
        raise HTTPException(503, "TracingManager not initialized")
    return {"service": tracing_manager.service_name, "enabled": tracing_manager.tracer is not None}

@router.get("/query", response_model=TraceQueryResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "tracing", "read"))])
async def query_trace(trace_id: str = Query(...)):
    logger.warning("Trace query endpoint called but not implemented")
    raise HTTPException(501, "Trace querying not implemented in this version")
