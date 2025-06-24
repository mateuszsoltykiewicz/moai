from pydantic import BaseModel, Field
from typing import Optional

class UpdateCheckResponse(BaseModel):
    update_available: bool = Field(..., description="Is there an update available?")
    current_version: str = Field(..., description="Current application version")
    latest_version: Optional[str] = Field(None, description="Latest available version")
    details: Optional[str] = Field(None, description="Additional details about the update")

    class Config:
        schema_extra = {
            "example": {
                "update_available": True,
                "current_version": "1.2.3",
                "latest_version": "1.3.0",
                "details": "Security and performance improvements."
            }
        }

class UpdateTriggerResponse(BaseModel):
    success: bool = Field(..., description="Whether the update was triggered successfully")
    message: Optional[str] = Field(None, description="Additional information or errors")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Update process started. Estimated downtime: 30s."
            }
        }
