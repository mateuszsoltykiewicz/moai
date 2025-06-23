"""
Pydantic schemas for DatabaseManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any

class DatabaseRecordCreate(BaseModel):
    id: str = Field(..., example="rec-001")
    Dict[str, Any]

class DatabaseRecordResponse(BaseModel):
    id: str
    Dict[str, Any]

    class Config:
        orm_mode = True
