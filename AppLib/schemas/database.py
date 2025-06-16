from typing import Any, Dict
from pydantic import BaseModel, Field

class DatabaseRecordCreate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Record data")

class DatabaseRecordResponse(BaseModel):
    id: str = Field(..., description="Record ID")
    data: Dict[str, Any] = Field(..., description="Record data")

class DatabaseRecordUpdate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Updated record data")