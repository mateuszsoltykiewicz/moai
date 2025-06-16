from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AlarmLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Alarm(BaseModel):
    """
    Represents an alarm or alert event in the system.
    """
    code: str = Field(..., description="Unique alarm code")
    message: str = Field(..., description="Human-readable description")
    level: AlarmLevel = Field(..., description="Severity level")
    timestamp: Optional[str] = Field(None, description="ISO8601 timestamp")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context/details")

    class Config:
        schema_extra = {
            "example": {
                "code": "DATABASE_CONNECTION_LOST",
                "message": "Database connection lost for more than 5 seconds.",
                "level": "critical",
                "timestamp": "2025-06-11T17:15:00Z",
                "details": {"host": "db1", "retry_count": 3}
            }
        }