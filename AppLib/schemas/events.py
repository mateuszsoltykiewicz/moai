from typing import Any, Dict, List, Optional, HttpUrl
from pydantic import BaseModel, Field

class EventPublishRequest(BaseModel):
    topic: str = Field(..., description="Event topic or channel")
    key: Optional[str] = Field(None, description="Optional event key")
    value: Dict[str, Any] = Field(..., description="Event payload")

class EventPublishResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class EventRecord(BaseModel):
    topic: str
    key: Optional[str]
    value: Dict[str, Any]
    offset: Optional[int] = None
    partition: Optional[int] = None
    timestamp: Optional[int] = None

class EventListResponse(BaseModel):
    events: List[EventRecord]

class WebhookSubscriptionRequest(BaseModel):
    topic: str = Field(..., description="Topic to subscribe to")
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Optional filter for event payloads")

class WebhookSubscriptionResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class WebhookEventDeliveryResponse(BaseModel):
    status: str