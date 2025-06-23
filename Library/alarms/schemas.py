"""
Pydantic schemas for AlarmsManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any

class Alarm(BaseModel):
    id: str
    source: str
    type: str
    details: Dict[str, Any]
    active: bool = True

class AlarmRaiseRequest(BaseModel):
    id: str = Field(..., example="alarm-001")
    source: str = Field(..., example="I2CManager")
    type: str = Field(..., example="hardware_fault")
    details: Dict[str, Any] = Field(default_factory=dict)

class AlarmClearRequest(BaseModel):
    id: str = Field(..., example="alarm-001")
