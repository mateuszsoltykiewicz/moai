from pydantic import BaseModel, Field, validator
from typing import Dict, Any

class I2CDeviceConfig(BaseModel):
    name: str
    address: int = Field(..., gt=0, le=127)
    type: str
    options: Dict[str, Any] = {}

class I2CControlRequest(BaseModel):
    device: str
    action: str = Field(..., regex="^(on|off)$")

    @validator('action')
    def action_must_be_on_off(cls, v):
        if v not in ['on', 'off']:
            raise ValueError("Action must be 'on' or 'off'")
        return v

class I2CStatusResponse(BaseModel):
    device: str
    status: str
    value: Any = None
