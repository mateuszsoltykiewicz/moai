from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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
