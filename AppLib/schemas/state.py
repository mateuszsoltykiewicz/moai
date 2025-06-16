from pydantic import BaseModel, Field
from typing import Optional

class AppStateSchema(BaseModel):
    status: str = Field(..., description="Current app state (e.g., running, paused, maintenance)")
    uptime_seconds: int = Field(..., description="App uptime in seconds")
    version: str = Field(..., description="App version")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional state details")

class AppStateUpdateRequest(BaseModel):
    status: str = Field(..., description="New desired app state")
    reason: Optional[str] = Field(None, description="Reason for state change")