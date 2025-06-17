from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class AppStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class AppStateSchema(BaseModel):
    status: AppStatus = Field(..., description="Current app state (e.g., running, paused, maintenance, error)")
    uptime_seconds: int = Field(..., ge=0, description="App uptime in seconds")
    version: str = Field(..., description="App version")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional state details")

    class Config:
        schema_extra = {
            "example": {
                "status": "running",
                "uptime_seconds": 3600,
                "version": "1.3.7",
                "details": {"db_connected": True, "active_users": 12}
            }
        }

class AppStateUpdateRequest(BaseModel):
    status: AppStatus = Field(..., description="New desired app state")
    reason: Optional[str] = Field(None, description="Reason for state change")

    class Config:
        schema_extra = {
            "example": {
                "status": "maintenance",
                "reason": "Scheduled database upgrade"
            }
        }
