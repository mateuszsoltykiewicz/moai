from pydantic import BaseModel, Field
from typing import Dict, Any

class HealthCheckDetail(BaseModel):
    status: str = Field(..., example="ok")
    details: Dict[str, Any] = Field(default_factory=dict)

class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok")
    checks: Dict[str, HealthCheckDetail]
    uptime_seconds: int = Field(..., example=12345)
    version: str = Field(..., example="1.2.3")
