from pydantic import BaseModel, Field
from typing import Dict, Optional

class KafkaProduceRequest(BaseModel):
    topic: str = Field(..., example="my.topic")
    key: Optional[str] = Field(None, example="message-key")
    value: str = Field(..., example='{"event": "login"}')
    headers: Optional[Dict[str, str]] = Field(None, example={"source": "api"})
