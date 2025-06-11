"""
Shared Pydantic schemas for API, messaging, and database interactions.

- All schemas are Pydantic models, providing type safety and validation.
- Each schema includes field constraints, documentation, and example data.
- Extend this file as your platform grows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, EmailStr

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

class KafkaMessageSchema(BaseModel):
    topic: str = Field(..., description="Kafka topic name")
    key: Optional[str] = Field(None, description="Message key")
    value: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: Optional[datetime] = Field(None, description="ISO8601 timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "events.device",
                    "key": "device-123",
                    "value": {"temperature": 22.5, "status": "active"},
                    "timestamp": "2025-06-11T17:15:00Z"
                }
            ]
        }
    }

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


# --- Utility: Generate JSON Schema (for docs, OpenAPI, etc.) ---

if __name__ == "__main__":
    import json
    print("UserSchema JSON Schema:")
    print(json.dumps(UserSchema.model_json_schema(), indent=2))
    print("Pet Discriminated Union JSON Schema:")
    from pydantic import schema_json_of
    print(schema_json_of(Pet, title='The Pet Schema', indent=2))
