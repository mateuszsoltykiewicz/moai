"""
SQLAlchemy async ORM models for DatabaseManager.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, JSON
from .schemas import DatabaseRecordCreate

Base = declarative_base()

class DatabaseRecord(Base):
    __tablename__ = "records"
    id = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=False)

    @classmethod
    def from_create(cls, record: DatabaseRecordCreate):
        return cls(id=record.id, data=record.data)
