"""
Metrics API Router

- Prometheus metrics endpoint
- Configurable RBAC (optional)
- Pre/post hooks for custom metrics or audit
- Default executions (Prometheus scrape)
- Comprehensive structured logging
"""

from fastapi import APIRouter, Depends, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics.core import REGISTRY
from core.tracing import AsyncTracer
from core.logging import logger
from api.dependencies import base_endpoint_processor, require_role
from typing import Dict, Any

tracer = AsyncTracer("applib-metrics").get_tracer()

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    include_in_schema=False  # Hide from OpenAPI docs
)

@router.get("")
async def prometheus_metrics(
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="metrics:get",
            pre_hook="api.hooks.metrics.before_metrics",
            post_hook="api.hooks.metrics.after_metrics",
            # Uncomment below to require RBAC for metrics endpoint (optional)
            # dependencies=[Depends(require_role("metrics.read"))]
        )
    ),
    request: Request = None
):
    """
    Prometheus scrape endpoint with:
    - Optional RBAC
    - Pre/post hooks for custom metrics or audit
    - Telemetry and logging
    """
    with tracer.start_as_current_span("metrics_endpoint"):
        logger.info("Serving Prometheus metrics scrape")
        # Pre-hook can inject or modify metrics if needed via context
        output = generate_latest(REGISTRY)
        # Post-hook can audit or log scrape events
        return Response(content=output, media_type=CONTENT_TYPE_LATEST)
