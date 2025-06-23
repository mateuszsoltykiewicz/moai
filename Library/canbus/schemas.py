"""
Pydantic schemas for CanbusManager.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class CanbusSensorConfig(BaseModel):
    name: str
    arbitration_id: int
    type: str
    options: Optional[dict] = None

class CanbusStreamResponse(BaseModel):
    sensor: str
    arbitration_id: int
    List[int]
    timestamp: float
