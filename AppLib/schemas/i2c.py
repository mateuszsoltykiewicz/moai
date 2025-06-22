from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class I2CCommandConfigRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    frequency: int = Field(..., example=400000)
    address: int = Field(..., example=0x48)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class I2CCommandQueueRequest(BaseModel):
    adapter_id: str = Field(..., example="i2c-1")
    commands: List[Dict[str, Any]] = Field(..., example=[{"cmd": "read", "length": 4}])

class I2CCommandResponse(BaseModel):
    adapter_id: str
    success: bool
    message: str
    data: Optional[List[int]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
