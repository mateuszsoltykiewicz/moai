from typing import List
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class LogLevelUpdateRequest(BaseModel):
    logger_name: str = Field(..., description="Logger name (use '' for root logger)")
    level: str = Field(..., description="New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

class LogLevelUpdateResponse(BaseModel):
    logger_name: str
    old_level: str
    new_level: str

class LoggerStatus(BaseModel):
    logger_name: str
    level: str

class LoggerListResponse(BaseModel):
    loggers: List[LoggerStatus]