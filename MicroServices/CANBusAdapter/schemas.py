from pydantic import BaseModel, Field
from typing import Optional

class SensorData(BaseModel):
    id: str = Field(..., example="sensor-001")
    value: float = Field(..., example=42.0)
    timestamp: float = Field(..., example=1625077800.0)
    status: str = Field(..., example="OK")

class SensorDataResponse(BaseModel):
    id: str
    value: float
    timestamp: float
    status: str
