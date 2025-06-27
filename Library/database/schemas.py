"""
Pydantic schemas for DatabaseManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any

class DatabaseRecordCreate(BaseModel):
    id: str = Field(..., example="rec-001")
    data: Dict[str, Any] = Field(..., description="Record data payload")

class DatabaseRecordResponse(BaseModel):
    id: str
    data: Dict[str, Any]

    class Config:
        orm_mode = True
