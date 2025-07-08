from pydantic import BaseModel
from typing import Optional, Dict

class KafkaConsumeResponse(BaseModel):
    topic: str
    key: Optional[str]
    value: str
    partition: int
    offset: int
    timestamp: int
    headers: Optional[Dict[str, str]]
