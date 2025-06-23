# config_server/schemas.py
from pydantic import BaseModel

class ConfigResponse(BaseModel):
    config: dict
    version: str

class ConfigUpdateEvent(BaseModel):
    service: str
