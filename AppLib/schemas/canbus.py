from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class CANBusStreamConfigRequest(BaseModel):
    adapter_id: str = Field(..., description="Unique CANBus adapter identifier")
    bitrate: int = Field(..., description="CAN bus bitrate in bits per second")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional CAN message filters")

class CANBusStreamConfigResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class CANBusStatusResponse(BaseModel):
    adapter_id: str
    status: str
    last_configured: Optional[str] = None
    details: Optional[Dict[str, Any]] = None