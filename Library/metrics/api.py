"""
API endpoints for MetricsManager.

- Exposes /metrics endpoint for Prometheus scrapes
"""

from fastapi import APIRouter, Response
from .manager import MetricsManager

router = APIRouter(prefix="/metrics", tags=["metrics"])

metrics_manager = MetricsManager()

@router.get("", include_in_schema=False)
async def prometheus_metrics():
    """
    Prometheus scrape endpoint.
    """
    output = metrics_manager.scrape()
    return Response(content=output, media_type="text/plain")
