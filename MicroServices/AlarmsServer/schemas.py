from pydantic import BaseModel, Field
from typing import Optional

class AlarmCreateRequest(BaseModel):
    id: str = Field(..., example="alarm-001")
    type: str = Field(..., example="FATAL")
    message: str = Field(..., example="Power failure detected")
    timestamp: float = Field(..., example=1625077800.0)
    active: bool = Field(default=True)

class AlarmDeleteRequest(BaseModel):
    id: str = Field(..., example="alarm-001")

class AlarmResponse(BaseModel):
    id: str
    type: str
    message: str
    timestamp: float
    active: bool
