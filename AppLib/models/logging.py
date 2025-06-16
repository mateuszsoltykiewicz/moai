from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    logger: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class LoggerStatus(BaseModel):
    name: str
    level: str
    handlers: List[str]
