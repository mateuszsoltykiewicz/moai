"""
API endpoints for TracingManager.

- Exposes /tracing/test-span for diagnostics
- Exposes /tracing/info for exporter status
"""

from fastapi import APIRouter, Request
from .manager import TracingManager
from .schemas import TraceInfo

router = APIRouter(prefix="/tracing", tags=["tracing"])

tracing_manager = TracingManager()

@router.get("/test-span")
async def test_span(request: Request):
    """
    Generate and return a test trace span for diagnostics.
    """
    tracer = tracing_manager.get_tracer()
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("user_agent", request.headers.get("user-agent", "unknown"))
        span.set_attribute("test", True)
        trace_id = format(span.get_span_context().trace_id, "x")
        span_id = format(span.get_span_context().span_id, "x")
        parent_span_id = (
            format(span.get_span_context().parent_span_id, "x")
            if getattr(span.get_span_context(), "parent_span_id", None) else None
        )
        attributes = getattr(span, "attributes", {})
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "attributes": attributes,
        "message": "Test span generated. Check your tracing backend."
    }

@router.get("/info")
async def tracing_info():
    """
    Returns basic tracing diagnostics and exporter status.
    """
    from opentelemetry.trace import get_tracer_provider
    provider = get_tracer_provider()
    try:
        exporters = getattr(provider, "_active_span_processor", None)
        exporter_info = str(exporters) if exporters else "unknown"
    except Exception:
        exporter_info = "unavailable"
    return {
        "service_name": "applib-tracing",
        "exporter": exporter_info,
        "otel_enabled": tracing_manager.tracer is not None
    }
