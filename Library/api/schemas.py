"""
Pydantic schemas for ApiManager (for future extensibility).
"""

from pydantic import BaseModel

class ApiStatusResponse(BaseModel):
    status: str
    message: str
