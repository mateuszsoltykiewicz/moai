"""
Pydantic schemas for KafkaManager.
"""

from pydantic import BaseModel, Field
from typing import Optional

class KafkaProduceRequest(BaseModel):
    topic: str = Field(..., example="my.topic")
    key: Optional[str] = Field(None, example="my-key")
    value: str = Field(..., example="{'event': 'login'}")

class KafkaConsumeResponse(BaseModel):
    topic: str
    key: Optional[str]
    value: str
    partition: int
    offset: int
    timestamp: int
