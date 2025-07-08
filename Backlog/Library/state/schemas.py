from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional

class StateResponse(BaseModel):
    key: str
    value: Any

class StateUpdateRequest(BaseModel):
    value: Optional[Any] = None
    updates: Optional[Dict[str, Any]] = None

    @validator('value', 'updates', pre=True)
    def check_at_least_one(cls, v, values):
        if values.get('value') is None and values.get('updates') is None:
            raise ValueError('Either value or updates must be provided')
        return v
