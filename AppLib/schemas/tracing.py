from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TracingStatusResponse(BaseModel):
    enabled: bool = Field(..., description="Is distributed tracing enabled?")
    exporter: Optional[str] = Field(None, description="Active tracing exporter (e.g., 'jaeger', 'otlp', 'zipkin')")
    service_name: Optional[str] = Field(None, description="Service name for traces")
    trace_id: Optional[str] = Field(None, description="Current trace ID, if available")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional tracing details or exporter config")

    class Config:
        schema_extra = {
            "example": {
                "enabled": True,
                "exporter": "jaeger",
                "service_name": "applib-core",
                "trace_id": "c0ffee1234567890",
                "details": {"sampling_rate": 1.0}
            }
        }
