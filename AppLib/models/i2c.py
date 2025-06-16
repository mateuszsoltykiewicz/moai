from pydantic import BaseModel, Field
from typing import Dict, Any

class I2CCommand(BaseModel):
    command: str = Field(..., description="I2C command type")
    address: int = Field(..., description="I2C device address")
    data: Dict[str, Any] = Field(default_factory=dict, description="Command payload")

class I2CConfig(BaseModel):
    bus_number: int = 1
    device_address: int