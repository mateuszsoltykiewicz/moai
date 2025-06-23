"""
Pydantic schemas for I2CManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class I2CDeviceConfig(BaseModel):
    name: str
    address: int
    type: str
    options: Optional[Dict[str, Any]] = None

class I2CControlRequest(BaseModel):
    device: str = Field(..., example="relay1")
    action: str = Field(..., example="on")  # "on" or "off"

class I2CStatusResponse(BaseModel):
    device: str
    status: str
    value: Optional[Any] = None
