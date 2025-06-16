from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, SecretStr
from typing import Dict

Base = declarative_base()

class DatabaseRecordDB(Base):
    __tablename__ = "records"
    id = Column(String, primary_key=True, index=True)
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
