from pydantic import BaseModel, Field
from typing import Optional

class PersistenceConfig(BaseModel):
    enabled: bool = Field(default=False)
    path: Optional[str] = Field(default="state_backups/latest_state.json")

class RoutersConfig(BaseModel):
    """
    Configuration schema for enabling/disabling routers (API modules).
    """
    canbus: bool = Field(default=False, description="Enable CANBus API router")
    database: bool = Field(default=False, description="Enable Database API router")
    i2c: bool = Field(default=False, description="Enable I2C API router")
    kafka: bool = Field(default=False, description="Enable Kafka API router")
    alarms: bool = Field(default=True, description="Enable Alarms API router")
    appstate: bool = Field(default=True, description="Enable AppState API router")
    audit: bool = Field(default=True, description="Enable Audit API router")
    auth: bool = Field(default=True, description="Enable Auth API router")
    config: bool = Field(default=True, description="Enable Config API router")
    events: bool = Field(default=True, description="Enable Events API router")
    health: bool = Field(default=True, description="Enable Health API router")
    logging: bool = Field(default=True, description="Enable Logging API router")
    metrics: bool = Field(default=True, description="Enable Metrics API router")
    mtls: bool = Field(default=True, description="Enable mTLS API router")
    rate_limiting: bool = Field(default=True, description="Enable Rate Limiting API router")
    secrets: bool = Field(default=True, description="Enable Secrets API router")
    tracing: bool = Field(default=True, description="Enable Tracing API router")
    updates: bool = Field(default=True, description="Enable Updates API router")

    class Config:
        schema_extra = {
            "example": {
                "canbus": True,
                "database": False,
                "i2c": False,
                "kafka": True,
                "alarms": True,
                "appstate": True,
                "audit": True,
                "auth": True,
                "config": True,
                "events": True,
                "health": True,
                "logging": True,
                "metrics": True,
                "mtls": True,
                "rate_limiting": True,
                "secrets": True,
                "tracing": True,
                "updates": True
            }
        }
