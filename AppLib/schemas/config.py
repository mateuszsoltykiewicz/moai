from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ConfigResponseSchema(BaseModel):
    config: Dict[str, Any] = Field(..., description="Current application configuration")

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="New configuration to apply")
    reason: str = Field(..., description="Reason for config update (for audit)")