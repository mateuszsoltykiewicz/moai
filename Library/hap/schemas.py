"""
Pydantic schemas for HAPManager.
"""

from pydantic import BaseModel, Field
from typing import List

class HAPAccessoryConfig(BaseModel):
    name: str
    component_name: str
    type: str

class HAPStatusResponse(BaseModel):
    bridge_name: str
    accessories: List[str]
    running: bool
