from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl

class EventPublishRequest(BaseModel):
    topic: str = Field(..., description="Event topic or channel")
    key: Optional[str] = Field(None, description="Optional event key")
    value: Dict[str, Any] = Field(..., description="Event payload")

    class Config:
        schema_extra = {
            "example": {
                "topic": "sensor.data",
                "key": "sensor-123",
                "value": {"temperature": 22.5, "unit": "C"}
            }
        }

class EventPublishResponse(BaseModel):
    success: bool = Field(..., description="Whether the event was published successfully")
    message: Optional[str] = Field(None, description="Additional information or errors")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Event published successfully"
            }
        }

class EventRecord(BaseModel):
    topic: str = Field(..., description="Event topic")
    key: Optional[str] = Field(None, description="Event key")
    value: Dict[str, Any] = Field(..., description="Event payload")
    offset: Optional[int] = Field(None, description="Message offset")
    partition: Optional[int] = Field(None, description="Partition number")
    timestamp: Optional[int] = Field(None, description="Event timestamp (epoch ms)")

    class Config:
        schema_extra = {
            "example": {
                "topic": "sensor.data",
                "key": "sensor-123",
                "value": {"temperature": 22.5, "unit": "C"},
                "offset": 123,
                "partition": 0,
                "timestamp": 1728850123456
            }
        }

class EventListResponse(BaseModel):
    events: List[EventRecord] = Field(..., description="List of event records")

class WebhookSubscriptionRequest(BaseModel):
    topic: str = Field(..., description="Topic to subscribe to")
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Optional filter for event payloads")

    class Config:
        schema_extra = {
            "example": {
                "topic": "alerts.critical",
                "url": "https://my-service/webhook",
                "filter": {"level": "critical"}
            }
        }

class WebhookSubscriptionResponse(BaseModel):
    success: bool = Field(..., description="Was the webhook subscription successful?")
    message: Optional[str] = Field(None, description="Additional information or errors")

class WebhookEventDeliveryResponse(BaseModel):
    status: str = Field(..., description="Delivery status, e.g. 'delivered', 'failed'")
