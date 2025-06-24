# models/schemas/events.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class EventPublishRequest(BaseModel):
    topic: str = Field(..., example="user.actions")
    key: Optional[str] = Field(None, example="user123")
    value: Dict[str, Any] = Field(..., example={"action": "login"})

class EventPublishResponse(BaseModel):
    success: bool
    message: str

class EventRecordResponse(BaseModel):
    id: UUID
    topic: str
    key: Optional[str] = None
    value: Dict[str, Any]
    timestamp: datetime
    partition: int
    offset: int

class EventListResponse(BaseModel):
    events: List[EventRecordResponse]

class WebhookSubscriptionRequest(BaseModel):
    topic: str = Field(..., example="user.actions")
    url: str = Field(..., example="https://example.com/webhook")
    filter: Optional[Dict[str, Any]] = Field(None, example={"action": "login"})

class WebhookSubscriptionResponse(BaseModel):
    success: bool
    subscription_id: UUID
    message: str

class WebhookEventDeliveryResponse(BaseModel):
    status: str
