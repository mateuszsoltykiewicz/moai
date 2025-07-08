"""
Enhanced schemas with status enumeration.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Literal

HealthStatus = Literal["ok", "degraded", "fail", "timeout"]

class HealthCheckDetail(BaseModel):
    status: HealthStatus = Field(..., example="ok")
    details: Dict[str, Any] = Field(default_factory=dict)

class HealthCheckResponse(BaseModel):
    status: HealthStatus = Field(..., example="ok")
    checks: Dict[str, HealthCheckDetail]
    uptime_seconds: float = Field(..., example=12345.67)
    version: str = Field(..., example="1.2.3")
