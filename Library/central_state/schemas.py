from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ServiceState(BaseModel):
    name: str
    version: str
    endpoints: Dict[str, str]
    last_heartbeat: datetime
    meta: Optional[Dict[str, Any]] = None
    status: str = Field(..., example="healthy")
