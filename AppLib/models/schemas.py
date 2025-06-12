"""
Shared Pydantic schemas for API, messaging, and database interactions.

- All schemas are Pydantic models, providing type safety and validation.
- Each schema includes field constraints, documentation, and example data.
- Extend this file as your platform grows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl

# --- Health & Status Schemas ---

class HealthCheckSchema(BaseModel):
    status: str = Field(..., description="Service health status, e.g. 'ok' or 'degraded'")
    uptime_seconds: int = Field(..., description="Seconds since service start")
    version: Optional[str] = Field(None, description="Service version string")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "ok", "uptime_seconds": 12345, "version": "1.2.3"}
            ]
        }
    }

# --- Messaging & Event Schemas ---

class KafkaProduceRequest(BaseModel):
    topic: str = Field(..., description="Kafka topic")
    key: Optional[str] = Field(None, description="Message key")
    value: Dict[str, Any] = Field(..., description="Message payload")
    partition: Optional[int] = Field(None, description="Partition (optional)")

class KafkaProduceResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class KafkaMessage(BaseModel):
    topic: str
    key: Optional[str]
    value: Dict[str, Any]
    offset: Optional[int] = None
    partition: Optional[int] = None
    timestamp: Optional[int] = None

class KafkaConsumeRequest(BaseModel):
    topic: str
    group_id: Optional[str] = None
    partition: Optional[int] = None
    offset: Optional[int] = None
    limit: int = 10
    auto_commit: bool = True
    offset_reset: Optional[str] = Field("latest", description="'earliest', 'latest', or 'none'")

class KafkaConsumeResponse(BaseModel):
    messages: List[KafkaMessage]

class KafkaTopicCreateRequest(BaseModel):
    topic: str
    num_partitions: int = 1
    replication_factor: int = 1
    configs: Optional[Dict[str, Any]] = None

class KafkaTopicCreateResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# --- Database Schemas ---

class UserSchema(BaseModel):
    id: Optional[int] = Field(None, description="User ID (auto-generated)")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., max_length=120, description="User email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 42,
                    "username": "alice",
                    "email": "alice@example.com",
                    "created_at": "2025-06-11T17:00:00Z"
                }
            ]
        }
    }

class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=120)
    password: str = Field(..., min_length=8)

# --- Nested/Relationship Example ---

class PostBase(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(..., description="Post content")

class UserWithPostsSchema(UserSchema):
    posts: List[PostBase] = Field(default_factory=list, description="List of user's posts")


# --- CANBus Schemas ---
class CANBusStreamConfigRequest(BaseModel):
    adapter_id: str = Field(..., description="Unique CANBus adapter identifier")
    bitrate: int = Field(..., description="CAN bus bitrate in bits per second")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional CAN message filters")

class CANBusStreamConfigResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class CANBusStatusResponse(BaseModel):
    adapter_id: str
    status: str
    last_configured: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# --- I2C Schemas ---
class I2CCommandConfigRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    gpio_pin: int = Field(..., example=17)
    mode: str = Field(..., example="output")
    initial_state: Optional[bool] = Field(None, example=True)

class I2CCommandQueueRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    commands: List[Dict[str, Any]] = Field(
        example=[{"command": "read", "address": 0x76}]
    )

class I2CCommandResponse(BaseModel):
    success: bool
    message: Optional[str]
    details: Optional[Dict[str, Any]]

# --- APP State schema

class AppStateSchema(BaseModel):
    status: str = Field(..., description="Current app state (e.g., running, paused, maintenance)")
    uptime_seconds: int = Field(..., description="App uptime in seconds")
    version: str = Field(..., description="App version")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional state details")

class AppStateUpdateRequest(BaseModel):
    status: str = Field(..., description="New desired app state")
    reason: Optional[str] = Field(None, description="Reason for state change")

# --- Pydantic schemas for audit events ---

class AuditEvent(BaseModel):
    id: str = Field(..., description="Unique audit event ID")
    user: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource affected")
    timestamp: datetime = Field(..., description="Timestamp of the event")
    details: Optional[dict] = Field(default_factory=dict, description="Additional event details")

class AuditEventCreate(BaseModel):
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource affected")
    details: Optional[dict] = Field(default_factory=dict, description="Additional event details")

# --- Config related schemas

class ConfigResponseSchema(BaseModel):
    config: Dict[str, Any] = Field(..., description="Current application configuration")

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="New configuration to apply")
    reason: str = Field(..., description="Reason for config update (for audit)")

# --- Database schemas ---

class DatabaseRecordCreate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Record data")

class DatabaseRecordResponse(BaseModel):
    id: str = Field(..., description="Record ID")
    data: Dict[str, Any] = Field(..., description="Record data")

class DatabaseRecordUpdate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Updated record data")

# --- Events related schemas ---

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

# --- Health checks schema

class HealthCheckSchema(BaseModel):
    status: str = Field(..., description="Overall health status: 'ok' or 'degraded' or 'fail'")
    uptime_seconds: int = Field(..., description="Application uptime in seconds")
    version: str = Field(..., description="Application version")
    checks: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Subsystem/component health details")

# --- Logging related schemas

class LogLevelUpdateRequest(BaseModel):
    logger_name: str = Field(..., description="Logger name (use '' for root logger)")
    level: str = Field(..., description="New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

class LogLevelUpdateResponse(BaseModel):
    logger_name: str
    old_level: str
    new_level: str

class LoggerStatus(BaseModel):
    logger_name: str
    level: str

class LoggerListResponse(BaseModel):
    loggers: List[LoggerStatus]

# --- mTLS schemas ---

class MTLSStatusResponse(BaseModel):
    mtls: bool = Field(..., description="Whether mTLS was used")
    client_cert: Optional[str] = Field(None, description="Client certificate info")
    message: Optional[str] = Field(None, description="Status message")

# --- Rate limiting schemas ---

class RateLimitConfigRequest(BaseModel):
    scope: str = Field(..., description="Scope for rate limiting (e.g., 'user', 'ip', 'global')")
    limit: int = Field(..., description="Max requests allowed in the period")
    period_seconds: int = Field(..., description="Period in seconds")

class RateLimitConfigResponse(BaseModel):
    scope: str
    limit: int
    period_seconds: int

class RateLimitStatusResponse(BaseModel):
    allowed: bool
    remaining: int
    reset_in: int

# --- Secrets schemas ---

class SecretCreateRequest(BaseModel):
    name: str = Field(..., description="Secret name (unique key)")
    value: str = Field(..., description="Secret value (will be stored securely)")
    description: Optional[str] = Field(None, description="Optional description")

class SecretUpdateRequest(BaseModel):
    value: str = Field(..., description="New secret value")
    description: Optional[str] = Field(None, description="Optional description")

class SecretResponse(BaseModel):
    name: str
    description: Optional[str] = None

class SecretRetrieveResponse(BaseModel):
    name: str
    value: str
    description: Optional[str] = None

# --- Open telemetry

class TracingStatusResponse(BaseModel):
    enabled: bool = Field(..., description="Is tracing enabled?")
    exporter: Optional[str] = Field(None, description="Active tracing exporter")
    service_name: Optional[str] = Field(None, description="Service name for traces")
    trace_id: Optional[str] = Field(None, description="Current trace ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional info")

# --- Update schemas

class UpdateCheckResponse(BaseModel):
    update_available: bool = Field(..., description="Is there an update available?")
    current_version: str = Field(..., description="Current application version")
    latest_version: Optional[str] = Field(None, description="Latest available version")
    details: Optional[str] = Field(None, description="Additional details about the update")

class UpdateTriggerResponse(BaseModel):
    success: bool = Field(..., description="Whether the update was triggered successfully")
    message: Optional[str] = Field(None, description="Additional information or errors")

# --- Utility: Generate JSON Schema (for docs, OpenAPI, etc.) ---

if __name__ == "__main__":
    import json
    print("UserSchema JSON Schema:")
    print(json.dumps(UserSchema.model_json_schema(), indent=2))
    print("Pet Discriminated Union JSON Schema:")
    from pydantic import schema_json_of
    print(schema_json_of(Pet, title='The Pet Schema', indent=2))
