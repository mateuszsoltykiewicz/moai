"""
Tracing API Router

- Exposes tracing diagnostics and test endpoints
- Uses OpenTelemetry and project AsyncTracer
- Pre/post hooks for extensibility
- RBAC ready
- Comprehensive logging and observability
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from core.tracing import AsyncTracer
from core.logging import logger
from api.dependencies import base_endpoint_processor, require_role
from typing import Dict, Any
import time

tracer = AsyncTracer("applib-tracing").get_tracer()

router = APIRouter(
    prefix="/tracing",
    tags=["tracing"],
    responses={403: {"description": "Forbidden"}}
)

@router.get(
    "/test-span",
    summary="Generate and return a test trace span",
    description="Creates a sample span and returns its trace context for diagnostics."
)
async def test_span(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="tracing:test_span",
            pre_hook="api.hooks.tracing.before_test_span",
            post_hook="api.hooks.tracing.after_test_span",
            # dependencies=[Depends(require_role("tracing.read"))]  # Uncomment for RBAC
        )
    ),
    request: Request = None
):
    """
    Generate a test span and return trace context.
    """
    start_time = time.monotonic()
    with tracer.start_as_current_span("test_span") as span:
        # Add some attributes for demonstration
        span.set_attribute("user_agent", request.headers.get("user-agent", "unknown"))
        span.set_attribute("test", True)
        trace_id = format(span.get_span_context().trace_id, "x")
        span_id = format(span.get_span_context().span_id, "x")
        parent_span_id = format(span.get_span_context().parent_span_id, "x") if span.get_span_context().parent_span_id else None
        attributes = span.attributes if hasattr(span, "attributes") else {}
        # Simulate some work
        time.sleep(0.05)
    duration = time.monotonic() - start_time
    logger.info(f"Tracing test span generated in {duration:.3f}s")
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "attributes": attributes,
        "message": "Test span generated. Check your tracing backend."
    }

@router.get(
    "/info",
    summary="Tracing diagnostics",
    description="Returns basic tracing diagnostics and exporter status."
)
async def tracing_info(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="tracing:info",
            # dependencies=[Depends(require_role("tracing.read"))]
        )
    )
):
    """
    Returns tracing diagnostics and exporter status.
    """
    # Example: You could expose exporter configuration, service name, etc.
    from opentelemetry.trace import get_tracer_provider
    provider = get_tracer_provider()
    try:
        exporters = getattr(provider, "_active_span_processor", None)
        exporter_info = str(exporters) if exporters else "unknown"
    except Exception:
        exporter_info = "unavailable"
    logger.info("Tracing diagnostics endpoint called")
    return {
        "service_name": "applib-tracing",
        "exporter": exporter_info,
        "otel_enabled": tracer is not None
    }
