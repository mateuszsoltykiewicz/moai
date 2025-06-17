from typing import List
from pydantic import BaseModel, Field
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogLevelUpdateRequest(BaseModel):
    logger_name: str = Field(..., description="Logger name (use '' for root logger)")
    level: LogLevel = Field(..., description="New log level")

    class Config:
        schema_extra = {
            "example": {
                "logger_name": "my.module",
                "level": "DEBUG"
            }
        }

class LogLevelUpdateResponse(BaseModel):
    logger_name: str = Field(..., description="Logger name")
    old_level: LogLevel = Field(..., description="Previous log level")
    new_level: LogLevel = Field(..., description="New log level")

    class Config:
        schema_extra = {
            "example": {
                "logger_name": "my.module",
                "old_level": "INFO",
                "new_level": "DEBUG"
            }
        }

class LoggerStatus(BaseModel):
    logger_name: str = Field(..., description="Logger name")
    level: LogLevel = Field(..., description="Current log level")

class LoggerListResponse(BaseModel):
    loggers: List[LoggerStatus] = Field(..., description="List of all logger statuses")
