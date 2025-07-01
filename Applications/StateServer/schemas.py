from pydantic import BaseModel, Field
from typing import Any, Optional

class StateResponse(BaseModel):
    key: str
    value: Any

class StateUpdateRequest(BaseModel):
    value: Any = Field(..., description="State value to set")
