from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class AppStateModel(BaseModel):
    version: int = Field(default=1, description="Schema version for migrations")
    service_ready: bool = Field(default=False)
    last_backup: Optional[datetime] = None
    connections: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    hardware_status: Dict[str, str] = Field(default_factory=dict)
    custom_state: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('version')
    def validate_version(cls, v):
        if v != 1:
            raise ValueError(f"Unsupported state version: {v}")
        return v

class PersistenceConfig(BaseModel):
    enabled: bool = Field(default=False)
    path: Optional[str] = Field(default="state_backups/latest_state.json")
