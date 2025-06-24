from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Event(BaseModel):
    id: str
    type: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]

class EventMetadata(BaseModel):
    event_id: str
    correlation_id: Optional[str]
    causation_id: Optional[str]
