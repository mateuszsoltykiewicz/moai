from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AuditEvent(BaseModel):
    id: str = Field(..., description="Unique audit event ID (UUID)")
    user: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource affected")
    timestamp: datetime = Field(..., description="Timestamp of the event (ISO8601)")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event details")

    class Config:
        schema_extra = {
            "example": {
                "id": "e8d5b7c0-3e2a-4b0a-b7f9-2c1e6d9a3e7f",
                "user": "admin",
                "action": "delete_user",
                "resource": "user/123",
                "timestamp": "2025-06-16T10:15:30Z",
                "details": {"reason": "user request"}
            }
        }

class AuditEventCreate(BaseModel):
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource affected")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event details")

    class Config:
        schema_extra = {
            "example": {
                "action": "delete_user",
                "resource": "user/123",
                "details": {"reason": "user request"}
            }
        }
