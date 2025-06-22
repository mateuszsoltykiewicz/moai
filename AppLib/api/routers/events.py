"""
Production-Grade Events API Router

- Secure event publishing to Kafka
- Webhook registration with persistent storage
- Configurable RBAC
- Pre/post hooks for validation and auditing
- Comprehensive observability (tracing, metrics, logging)
- Async background task processing
"""

from fastapi import ( 
  APIRouter, 
  Depends, 
  status, 
  Body, 
  Request, 
  BackgroundTasks, 
  Query, 
  HTTPException )
from typing import List, Dict, Any, Optional
from uuid import UUID
from core.tracing import AsyncTracer
from metrics.events import record_event_operation
from core.logging import logger
from api.dependencies import base_endpoint_processor, require_role, get_db_session
from services.events import EventService, WebhookService
from schemas.events import (
    EventPublishRequest,
    EventPublishResponse,
    EventRecordResponse,
    EventListResponse,
    WebhookSubscriptionRequest,
    WebhookSubscriptionResponse,
    WebhookEventDeliveryResponse
)
from exceptions.core import ServiceUnavailableError, NotFoundError
import time
import json

tracer = AsyncTracer("applib-events").get_tracer()

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        503: {"description": "Service unavailable"}
    }
)

@router.post(
    "/publish",
    response_model=EventPublishResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish an event"
)
async def publish_event(
    background_tasks: BackgroundTasks,
    req: EventPublishRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="events:publish",
            pre_hook="api.hooks.events.validate_event_publish",
            post_hook="api.hooks.events.audit_event_publish",
            dependencies=[Depends(require_role("events.publish"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Publish an event to the event streaming system
    - RBAC: events.publish
    - Pre-hook: Validate event structure
    - Post-hook: Audit event publishing
    - Webhook delivery via background tasks
    """
    start_time = time.monotonic()
    try:
        # Pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        
        with tracer.start_as_current_span("event_publish"):
            # Publish to Kafka
            event_service = EventService(db)
            await event_service.publish(
                topic=req.topic,
                key=req.key,
                value=req.value
            )
            
            # Trigger webhook delivery
            webhook_service = WebhookService(db)
            background_tasks.add_task(
                webhook_service.deliver_to_webhooks,
                topic=req.topic,
                event_data={
                    "topic": req.topic,
                    "key": req.key,
                    "value": req.value
                }
            )
        
        duration = time.monotonic() - start_time
        record_event_operation("publish", duration)
        logger.info(f"Event published to {req.topic} in {duration:.3f}s")
        
        return EventPublishResponse(
            success=True,
            message="Event published and webhooks triggered"
        )
    except ServiceUnavailableError:
        logger.error("Event publishing service unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event service is currently unavailable"
        )

@router.get(
    "",
    response_model=EventListResponse,
    summary="List recent events"
)
async def list_events(
    topic: str = Query(..., description="Event topic"),
    key_filter: Optional[str] = Query(None, description="Filter by event key"),
    value_filter: Optional[str] = Query(None, description="JSON-encoded filter for event payload"),
    limit: int = Query(10, ge=1, le=100, description="Max number of events to fetch"),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="events:list",
            dependencies=[Depends(require_role("events.read"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    List recent events from a topic
    - RBAC: events.read
    - Supports filtering by key and value
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("event_list"):
            event_service = EventService(db)
            events = await event_service.list_events(
                topic=topic,
                key_filter=key_filter,
                value_filter=json.loads(value_filter) if value_filter else None,
                limit=limit
            )
        
        duration = time.monotonic() - start_time
        record_event_operation("list", duration, count=len(events))
        logger.info(f"Listed {len(events)} events from {topic} in {duration:.3f}s")
        
        return EventListResponse(events=events)
    except ServiceUnavailableError:
        logger.error("Event listing service unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event service is currently unavailable"
        )

@router.post(
    "/webhooks",
    response_model=WebhookSubscriptionResponse,
    summary="Register a webhook for a topic"
)
async def subscribe_webhook(
    req: WebhookSubscriptionRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="events:webhook_subscribe",
            dependencies=[Depends(require_role("events.webhook.manage"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Register a webhook endpoint for a topic
    - RBAC: events.webhook.manage
    - Persistent storage of webhook config
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("webhook_subscribe"):
            webhook_service = WebhookService(db)
            subscription = await webhook_service.create_subscription(
                topic=req.topic,
                url=req.url,
                user_id=context["user"].sub,
                filters=req.filter
            )
        
        duration = time.monotonic() - start_time
        record_event_operation("webhook_subscribe", duration)
        logger.info(f"Webhook registered for {req.topic} in {duration:.3f}s")
        
        return WebhookSubscriptionResponse(
            success=True,
            subscription_id=subscription.id,
            message="Webhook subscribed"
        )
    except ServiceUnavailableError:
        logger.error("Webhook service unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook service is currently unavailable"
        )

@router.delete(
    "/webhooks/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister a webhook"
)
async def unsubscribe_webhook(
    subscription_id: UUID,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="events:webhook_unsubscribe",
            dependencies=[Depends(require_role("events.webhook.manage"))]
        )
    ),
    db=Depends(get_db_session)
):
    """
    Unregister a webhook subscription
    - RBAC: events.webhook.manage
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("webhook_unsubscribe"):
            webhook_service = WebhookService(db)
            await webhook_service.delete_subscription(subscription_id, context["user"].sub)
        
        duration = time.monotonic() - start_time
        record_event_operation("webhook_unsubscribe", duration)
        logger.info(f"Webhook {subscription_id} unsubscribed in {duration:.3f}s")
    except NotFoundError:
        logger.warning(f"Webhook {subscription_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found"
        )
    except ServiceUnavailableError:
        logger.error("Webhook service unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook service is currently unavailable"
        )

@router.post(
    "/webhooks/test",
    response_model=WebhookEventDeliveryResponse,
    summary="Test webhook endpoint (internal use)",
    include_in_schema=False  # Hide from public docs
)
async def test_webhook_endpoint(
    request: Request
):
    """
    Internal webhook testing endpoint
    - Not exposed in public API docs
    - For development and testing purposes
    """
    payload = await request.json()
    logger.debug(f"Test webhook received payload: {payload}")
    return WebhookEventDeliveryResponse(status="ok")
