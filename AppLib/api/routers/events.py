"""
Events API Router

- Publish/query events (Kafka or other event backend)
- Register webhooks for topics (with filtering)
- Deliver events to webhooks on publish
- All endpoints are async, schema-driven, and secured
"""

from fastapi import APIRouter, Depends, status, Query, Request, BackgroundTasks
from typing import List, Optional, Dict, Any
from models.schemas import (
    EventPublishRequest, EventPublishResponse,
    EventRecord, EventListResponse,
    WebhookSubscriptionRequest, WebhookSubscriptionResponse,
    WebhookEventDeliveryResponse
)
from api.dependencies import get_current_user
from api.main import APIException
from sessions.kafka import get_kafka_producer, get_kafka_consumer
import httpx
import json

router = APIRouter(tags=["events"])

# In-memory registry for webhooks: {topic: [ {url, filter}, ... ]}
WEBHOOK_REGISTRY: Dict[str, List[Dict[str, Any]]] = {}

def event_matches_filter(event_value: Dict[str, Any], filter_: Optional[Dict[str, Any]]) -> bool:
    """Simple filter: all key-value pairs in filter_ must match event_value"""
    if not filter_:
        return True
    for k, v in filter_.items():
        if event_value.get(k) != v:
            return False
    return True

async def deliver_event_to_webhooks(topic: str, event: Dict[str, Any], background_tasks: BackgroundTasks):
    """Deliver event to all registered webhooks for the topic, applying filters."""
    for webhook in WEBHOOK_REGISTRY.get(topic, []):
        if event_matches_filter(event["value"], webhook.get("filter")):
            background_tasks.add_task(send_webhook, webhook["url"], event)

async def send_webhook(url: str, event: Dict[str, Any]):
    """Send event to webhook endpoint asynchronously."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=event, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            # In production, log or alert on failed webhook deliveries
            pass

@router.post(
    "/publish",
    response_model=EventPublishResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish an event"
)
async def publish_event(
    req: EventPublishRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """
    Publish an event to the event streaming system (e.g., Kafka) and trigger webhooks.
    """
    try:
        producer = await get_kafka_producer()
        value_bytes = json.dumps(req.value).encode("utf-8")
        key_bytes = req.key.encode("utf-8") if req.key else None
        await producer.send_and_wait(req.topic, value=value_bytes, key=key_bytes)
        # Deliver to registered webhooks (fire-and-forget)
        event_dict = {"topic": req.topic, "key": req.key, "value": req.value}
        await deliver_event_to_webhooks(req.topic, event_dict, background_tasks)
        return EventPublishResponse(success=True, message="Event published and webhooks triggered.")
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to publish event.",
            details={"error": str(e)}
        )

@router.get(
    "/list",
    response_model=EventListResponse,
    summary="List recent events"
)
async def list_events(
    topic: str = Query(..., description="Event topic"),
    key: Optional[str] = Query(None, description="Filter by event key"),
    value_filter: Optional[str] = Query(None, description="JSON-encoded filter for event payload"),
    limit: int = Query(10, ge=1, le=100, description="Max number of events to fetch"),
    user=Depends(get_current_user)
):
    """
    List recent events from a topic (using Kafka consumer), with optional filtering.
    """
    try:
        consumer = await get_kafka_consumer(topic)
        events = []
        async for msg in consumer:
            value = json.loads(msg.value)
            if key and (msg.key is None or msg.key.decode("utf-8") != key):
                continue
            if value_filter:
                filter_dict = json.loads(value_filter)
                if not event_matches_filter(value, filter_dict):
                    continue
            events.append(EventRecord(
                topic=msg.topic,
                key=msg.key.decode("utf-8") if msg.key else None,
                value=value,
                offset=msg.offset,
                partition=msg.partition,
                timestamp=msg.timestamp
            ))
            if len(events) >= limit:
                break
        await consumer.stop()
        return EventListResponse(events=events)
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to list events.",
            details={"error": str(e)}
        )

@router.post(
    "/webhook/subscribe",
    response_model=WebhookSubscriptionResponse,
    summary="Register a webhook for a topic"
)
async def subscribe_webhook(
    req: WebhookSubscriptionRequest,
    user=Depends(get_current_user)
):
    """
    Register a webhook endpoint for a topic, with optional filtering.
    """
    topic = req.topic
    webhook = {"url": str(req.url), "filter": req.filter}
    if topic not in WEBHOOK_REGISTRY:
        WEBHOOK_REGISTRY[topic] = []
    # Prevent duplicate registration
    if webhook not in WEBHOOK_REGISTRY[topic]:
        WEBHOOK_REGISTRY[topic].append(webhook)
    return WebhookSubscriptionResponse(success=True, message="Webhook subscribed.")

@router.post(
    "/webhook",
    response_model=WebhookEventDeliveryResponse,
    summary="Webhook endpoint (for testing, not for production use)"
)
async def webhook_endpoint(
    request: Request
):
    """
    Example webhook endpoint to receive events (for testing).
    """
    payload = await request.json()
    # In production, validate signature, log, or process event as needed
    return WebhookEventDeliveryResponse(status="ok")
