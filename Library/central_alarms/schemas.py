from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class CentralAlarm(BaseModel):
    id: str
    source: str
    type: str
    details: Dict[str, Any]
    active: bool = True
    raised_at: datetime = Field(default_factory=datetime.utcnow)
    cleared_at: Optional[datetime] = None

class AlarmRaiseRequest(BaseModel):
    id: str
    source: str
    type: str
    details: Dict[str, Any]

class AlarmClearRequest(BaseModel):
    id: str
    cleared_at: Optional[datetime] = None
