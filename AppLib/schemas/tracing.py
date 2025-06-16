from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TracingStatusResponse(BaseModel):
    enabled: bool = Field(..., description="Is tracing enabled?")
    exporter: Optional[str] = Field(None, description="Active tracing exporter")
    service_name: Optional[str] = Field(None, description="Service name for traces")
    trace_id: Optional[str] = Field(None, description="Current trace ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional info")