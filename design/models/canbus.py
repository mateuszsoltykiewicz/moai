from pydantic import BaseModel, Field
from typing import List

class CANBusMessage(BaseModel):
    arbitration_id: int = Field(..., description="CAN message ID")
    data: List[int] = Field(..., description="Payload bytes")
    timestamp: float = Field(..., description="Message timestamp")
    is_error_frame: bool = Field(default=False)
    is_remote_frame: bool = Field(default=False)

class CANBusConfig(BaseModel):
    channel: str
    bitrate: int
    interface: str = "socketcan"
    filters: Optional[List[Dict[str, Any]]] = None