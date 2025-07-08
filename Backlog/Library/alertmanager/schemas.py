from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class Alert(BaseModel):
    labels: Dict[str, str] = Field(..., 
        example={"alertname": "HighLatency", "service": "api"})
    annotations: Optional[Dict[str, str]] = Field(None,
        example={"description": "Latency above 500ms"})
    startsAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    endsAt: Optional[datetime] = None
    generatorURL: Optional[str] = None

class Silence(BaseModel):
    matchers: List[Dict[str, str]] = Field(...,
        example=[{"name": "alertname", "value": "HighLatency"}])
    startsAt: datetime = Field(...)
    endsAt: datetime = Field(...)
    createdBy: str = Field(...)
    comment: str = Field(...)
    id: Optional[str] = None

class AlertManagerHealth(BaseModel):
    status: str
