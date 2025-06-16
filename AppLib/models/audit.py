from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict

Base = declarative_base()

class AuditEventDB(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True, index=True)
    user = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)

class AuditEvent(BaseModel):
    id: str
    user: str
    action: str
    resource: Optional[str]
    timestamp: datetime
    details: Optional[Dict] = Field(default_factory=dict)
