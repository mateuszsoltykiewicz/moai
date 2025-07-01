from pydantic import BaseModel
from typing import Dict

class ServiceInfo(BaseModel):
    name: str
    status: str

class ServiceListResponse(BaseModel):
    services: Dict[str, str]
