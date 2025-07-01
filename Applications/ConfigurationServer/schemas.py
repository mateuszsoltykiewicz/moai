from pydantic import BaseModel, Field
from typing import Dict, Any

class ConfigQueryRequest(BaseModel):
    service: str = Field(..., example="AlarmsServer")

class ConfigResponse(BaseModel):
    service: str
    version: str
    config: Dict[str, Any]
