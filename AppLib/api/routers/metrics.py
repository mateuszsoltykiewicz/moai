"""
Metrics API Router

- Exposes custom Prometheus metrics for internal dashboards (authenticated)
- Prometheus /metrics endpoint is exposed globally via Instrumentator in main.py
- Aggregates metrics from /metrics modules (adapters, database, kafka, app, etc.)
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from api.dependencies import get_current_user

# Import custom metrics from your metrics modules
from metrics.adapters import (
    I2C_COMMANDS_TOTAL, I2C_ERRORS_TOTAL,
    CANBUS_MESSAGES_TOTAL, CANBUS_ERRORS_TOTAL
)
from metrics.database import DB_QUERIES_TOTAL, DB_ERRORS_TOTAL
from metrics.kafka import (
    KAFKA_MESSAGES_PRODUCED, KAFKA_MESSAGES_CONSUMED, KAFKA_ERRORS_TOTAL
)
from metrics.app import update_uptime

router = APIRouter(tags=["metrics"])

@router.get(
    "/custom",
    summary="Custom Prometheus metrics (internal use)",
    response_class=Response,
    responses={200: {"content": {"text/plain": {}}}}
)
async def custom_metrics(user=Depends(get_current_user)):
    """
    Expose custom application and hardware metrics (for internal dashboards).
    """
    # Update any dynamic metrics before scraping (e.g., uptime)
    update_uptime()
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
