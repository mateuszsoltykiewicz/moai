from typing import Optional
from pydantic import BaseModel, Field

class HealthCheckSchema(BaseModel):
    status: str = Field(..., description="Service health status, e.g. 'ok' or 'degraded'")
    uptime_seconds: int = Field(..., description="Seconds since service start")
    version: Optional[str] = Field(None, description="Service version string")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "ok", "uptime_seconds": 12345, "version": "1.2.3"}
            ]
        }
    }