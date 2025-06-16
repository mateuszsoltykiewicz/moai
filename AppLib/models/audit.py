from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AuditEventDB(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True, index=True)
    user = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
