from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Session(BaseModel):
    id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: float = Field(..., description="Session creation timestamp")
    updated_at: float = Field(..., description="Session last update timestamp")
    expires_at: Optional[float] = Field(None, description="Session expiration timestamp")

class SessionCreateRequest(BaseModel):
    id: str = Field(..., example="session-001")
    data: Dict[str, Any] = Field(default_factory=dict)
    expires_in: Optional[int] = Field(None, description="Session TTL in seconds")

class SessionUpdateRequest(BaseModel):
    data: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    expires_in: Optional[int] = None
