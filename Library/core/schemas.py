"""
Pydantic schemas for CoreManager status and API.
"""

from pydantic import BaseModel
from typing import Dict, Any

class CoreStatusResponse(BaseModel):
    running: bool
    state: Dict[str, Any]
