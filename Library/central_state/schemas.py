from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime

class ServiceState(BaseModel):
    name: str = Field(..., min_length=3, max_length=64)
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")  # semver validation
    endpoints: Dict[str, str] = Field(..., min_items=1)
    last_heartbeat: datetime
    meta: Optional[Dict[str, Any]] = None
    status: str = Field("healthy", example="healthy")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["healthy", "degraded", "stale", "offline"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return v
