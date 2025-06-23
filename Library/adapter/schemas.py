"""
Pydantic schemas for AdapterManager.
"""

from pydantic import BaseModel
from typing import Dict

class AdapterInfo(BaseModel):
    type: str
    class_name: str

class AdapterConfig(BaseModel):
    type: str
    config: Dict[str, Any]
