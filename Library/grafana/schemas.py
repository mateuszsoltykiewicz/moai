from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class DashboardResponse(BaseModel):
    dashboard: Dict[str, Any]
    meta: Dict[str, Any]

class Annotation(BaseModel):
    time: int
    text: str
    tags: Optional[List[str]] = None

class AlertResponse(BaseModel):
    state: str
    title: str
    message: str
