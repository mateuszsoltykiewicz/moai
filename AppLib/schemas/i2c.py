from pydantic import BaseModel, Field
from typing import Optional

class I2CCommandConfigRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    gpio_pin: int = Field(..., example=17)
    mode: str = Field(..., example="output")
    initial_state: Optional[bool] = Field(None, example=True)

class I2CCommandQueueRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    commands: List[Dict[str, Any]] = Field(
        example=[{"command": "read", "address": 0x76}]
    )

class I2CCommandResponse(BaseModel):
    success: bool
    message: Optional[str]
    details: Optional[Dict[str, Any]]