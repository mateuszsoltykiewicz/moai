from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ServiceStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"

class HealthCheckSchema(BaseModel):
    status: ServiceStatus = Field(..., description="Service health status: 'ok', 'degraded', or 'error'")
    uptime_seconds: int = Field(..., ge=0, description="Seconds since service start")
    version: Optional[str] = Field(None, description="Service version string")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "uptime_seconds": 12345,
                "version": "1.2.3"
            }
        }
