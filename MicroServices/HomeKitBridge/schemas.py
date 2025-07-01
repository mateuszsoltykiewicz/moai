from pydantic import BaseModel, Field
from typing import List

class Accessory(BaseModel):
    id: str = Field(..., example="sensor-001")
    name: str = Field(..., example="Living Room Temp")
    type: str = Field(..., example="TemperatureSensor")
    status: str = Field(..., example="online")

class AccessoryListResponse(BaseModel):
    accessories: List[Accessory]
