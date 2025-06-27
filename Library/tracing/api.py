from fastapi import APIRouter, HTTPException, Query
from .manager import TracingManager
from .schemas import TraceQueryResponse
from .exceptions import TraceNotFoundError

router = APIRouter(prefix="/tracing", tags=["tracing"])
tracing_manager: TracingManager = None  # Should be initialized at app startup

@router.get("/status")
async def tracing_status():
    if not tracing_manager:
        raise HTTPException(503, "TracingManager not initialized")
    return {"service": tracing_manager.service_name, "enabled": tracing_manager.tracer is not None}

@router.get("/query", response_model=TraceQueryResponse)
async def query_trace(trace_id: str = Query(...)):
    # In production, integrate with your tracing backend (Jaeger, etc.)
    raise HTTPException(501, "Trace querying not implemented in this stub")
