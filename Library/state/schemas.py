"""
Pydantic schemas for StateManager.
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional

class StateResponse(BaseModel):
    key: str
    value: Any

class StateUpdateRequest(BaseModel):
    value: Any
    updates: Optional[Dict[str, Any]] = None
