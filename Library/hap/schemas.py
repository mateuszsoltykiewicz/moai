from pydantic import BaseModel, Field
from typing import List, Literal

class HAPAccessoryConfig(BaseModel):
    name: str = Field(..., min_length=3)
    component_name: str
    type: Literal["sensor", "switch", "light"] = Field(..., example="sensor")

class HAPStatusResponse(BaseModel):
    bridge_name: str
    accessories: List[str]  # Format: "name:status"
    running: bool
