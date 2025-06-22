from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, SecretStr
from typing import Dict
from uuid import UUID, uuid4

Base = declarative_base()

class DatabaseRecordDB(Base):
    __tablename__ = "records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    data = Column(JSON, nullable=False)

class DatabaseRecord(BaseModel):
    id: str
    data: Dict

class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str
    url: str  # e.g. "postgresql+asyncpg://user:pass@host/db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
