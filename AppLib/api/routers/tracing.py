from fastapi import APIRouter, Depends
from models.schemas import TracingStatusResponse
from api.dependencies import get_current_user
from adapters.tracing import TracingAdapter
from metrics.tracing import (
    TRACES_STARTED, TRACES_COMPLETED, TRACING_ERRORS, observe_span_duration
)
from opentelemetry import trace
import time

router = APIRouter(tags=["tracing"])

@router.get(
    "/status",
    response_model=TracingStatusResponse,
    summary="Check tracing status"
)
async def tracing_status(user=Depends(get_current_user)):
    provider = trace.get_tracer_provider()
    enabled = provider is not None
    exporter = None
    service_name = None
    trace_id = TracingAdapter().get_current_trace_id()
    details = {}
    if enabled:
        try:
            span_processors = getattr(provider, "_active_span_processor", None)
            if span_processors:
                exporter = span_processors.span_processors[0].__class__.__name__
            resource = getattr(provider, "resource", None)
            if resource and "service.name" in resource.attributes:
                service_name = resource.attributes["service.name"]
        except Exception:
            pass
        details = {"provider": str(type(provider))}
    return TracingStatusResponse(
        enabled=enabled,
        exporter=exporter,
        service_name=service_name,
        trace_id=trace_id,
        details=details
    )

@router.get(
    "/demo-span",
    summary="Create a custom trace span (demo)"
)
async def tracing_demo_span(user=Depends(get_current_user)):
    tracer = TracingAdapter()
    TRACES_STARTED.inc()
    start = time.time()
    try:
        with tracer.start_span("demo-span"):
            # Simulate work
            import asyncio
            await asyncio.sleep(0.1)
        TRACES_COMPLETED.inc()
    except Exception:
        TRACING_ERRORS.inc()
        raise
    finally:
        observe_span_duration(start, time.time())
    return {"message": "Custom trace span created (check your tracing backend)."}

