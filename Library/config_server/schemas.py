from pydantic import BaseModel
from typing import Dict, Any

class ConfigResponse(BaseModel):
    config: Dict[str, Any]
    version: str
    metadata: Dict[str, str] = {}

class ConfigUpdateEvent(BaseModel):
    service: str
    version: str = ""
