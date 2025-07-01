from sqlalchemy import Column, String, DateTime, Integer
from Library.database import Base
from datetime import datetime

class ExceptionRecord(Base):
    __tablename__ = "exceptions"
    id = Column(Integer, primary_key=True, index=True)
    exception_name = Column(String, index=True)
    service = Column(String, index=True)
    status = Column(String, index=True)
    last_change = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
