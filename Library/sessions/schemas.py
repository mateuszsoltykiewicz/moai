"""
Pydantic schemas for SessionsManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Session(BaseModel):
    id: str
    Dict[str, Any]
    active: bool = True

class SessionCreateRequest(BaseModel):
    id: str = Field(..., example="session-001")
    Dict[str, Any] = Field(default_factory=dict)

class SessionUpdateRequest(BaseModel):
    Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
