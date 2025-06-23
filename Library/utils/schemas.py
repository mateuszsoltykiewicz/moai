"""
Pydantic schemas for UtilsManager (for future extensibility).
"""

from pydantic import BaseModel

class StatusResponse(BaseModel):
    status: str
    message: str
