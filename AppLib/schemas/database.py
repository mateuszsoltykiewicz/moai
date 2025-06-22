from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import UUID

class ConfigResponseSchema(BaseModel):
    config: Dict[str, Any] = Field(..., description="Current application configuration")

    class Config:
        schema_extra = {
            "example": {
                "config": {
                    "database": {"host": "db.example.com", "port": 5432},
                    "auth": {"enabled": True},
                    "kafka": {"bootstrap_servers": "kafka:9092"}
                }
            }
        }

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="New configuration to apply")
    reason: str = Field(..., description="Reason for config update (for audit)")

    class Config:
        schema_extra = {
            "example": {
                "config": {
                    "auth": {"enabled": False}
                },
                "reason": "Disabling auth for maintenance window"
            }
        }

class DatabaseRecordCreate(BaseModel):
     dict = Field(..., example={"key": "value"})

class DatabaseRecordResponse(BaseModel):
    id: UUID
    dict