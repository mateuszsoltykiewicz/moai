from pydantic import BaseModel
from datetime import datetime

class ExceptionCreate(BaseModel):
    exception_name: str
    service: str
    status: str
    last_change: datetime

class ExceptionRead(BaseModel):
    id: int
    exception_name: str
    service: str
    status: str
    last_change: datetime
    created_at: datetime
    class Config:
        orm_mode = True
