from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class KafkaPublishRequest(BaseModel):
    topic: str = Field(..., example="my.topic")
    key: Optional[str] = Field(None, example="my-key")
    value: Dict[str, Any] = Field(..., example={"event": "login"})

class KafkaPublishResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class KafkaListMessagesResponse(BaseModel):
    messages: List[Dict[str, Any]]
