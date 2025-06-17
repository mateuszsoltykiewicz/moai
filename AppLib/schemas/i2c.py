from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class I2CMode(str, Enum):
    INPUT = "input"
    OUTPUT = "output"

class I2CCommandConfigRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1", description="Unique I2C adapter identifier")
    gpio_pin: int = Field(..., example=17, description="GPIO pin number")
    mode: I2CMode = Field(..., example="output", description="GPIO mode: input or output")
    initial_state: Optional[bool] = Field(None, example=True, description="Initial state for output mode")

class I2CCommand(BaseModel):
    command: str = Field(..., description="I2C command type, e.g., 'read' or 'write'")
    address: int = Field(..., description="I2C device address")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command payload")

class I2CCommandQueueRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1", description="Unique I2C adapter identifier")
    commands: List[I2CCommand] = Field(
        ..., 
        description="List of I2C commands to queue",
        example=[{"command": "read", "address": 0x76}]
    )

class I2CCommandResponse(BaseModel):
    success: bool = Field(..., description="Whether the command(s) were successful")
    message: Optional[str] = Field(None, description="Human-readable status or error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional result or error details")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Command executed successfully",
                "details": {"data": [12, 34]}
            }
        }
