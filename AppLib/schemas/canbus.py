from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class CANBusStatus(str, Enum):
    CONFIGURED = "configured"
    ERROR = "error"
    INITIALIZING = "initializing"

class CANFilter(BaseModel):
    can_id: int = Field(..., description="CAN message ID to filter")
    can_mask: int = Field(..., description="CAN mask for filtering")

class CANBusStreamConfigRequest(BaseModel):
    adapter_id: str = Field(..., description="Unique CANBus adapter identifier")
    bitrate: int = Field(..., ge=125000, le=1000000, description="CAN bus bitrate in bits per second (125k-1M)")
    filters: Optional[List[CANFilter]] = Field(
        default=None,
        description="Optional list of CAN message filters"
    )

class CANBusStreamConfigResponse(BaseModel):
    success: bool = Field(..., description="Was the configuration successful?")
    status_code: int = Field(200, description="HTTP status code")
    message: Optional[str] = Field(
        None,
        description="Human-readable status message"
    )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "CANBus configured successfully"
            }
        }

class CANBusStatusResponse(BaseModel):
    adapter_id: str = Field(..., description="Unique CANBus adapter identifier")
    status: CANBusStatus = Field(..., description="Current status of the CANBus adapter")
    last_configured: Optional[datetime] = Field(
        None,
        description="Last successful configuration timestamp"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error details if status=error"
    )
    active_filters: Optional[List[CANFilter]] = Field(
        None,
        description="Currently active message filters"
    )

    class Config:
        schema_extra = {
            "example": {
                "adapter_id": "canbus-1",
                "status": "configured",
                "last_configured": "2025-06-16T10:15:30Z",
                "error_message": None,
                "active_filters": [{"can_id": 291, "can_mask": 2047}]
            }
        }
