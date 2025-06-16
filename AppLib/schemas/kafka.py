from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class KafkaProduceRequest(BaseModel):
    topic: str = Field(..., description="Kafka topic")
    key: Optional[str] = Field(None, description="Message key")
    value: Dict[str, Any] = Field(..., description="Message payload")
    partition: Optional[int] = Field(None, description="Partition (optional)")

class KafkaProduceResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class KafkaMessage(BaseModel):
    topic: str
    key: Optional[str]
    value: Dict[str, Any]
    offset: Optional[int] = None
    partition: Optional[int] = None
    timestamp: Optional[int] = None

class KafkaConsumeRequest(BaseModel):
    topic: str
    group_id: Optional[str] = None
    partition: Optional[int] = None
    offset: Optional[int] = None
    limit: int = 10
    auto_commit: bool = True
    offset_reset: Optional[str] = Field("latest", description="'earliest', 'latest', or 'none'")

class KafkaConsumeResponse(BaseModel):
    messages: List[KafkaMessage]

class KafkaTopicCreateRequest(BaseModel):
    topic: str
    num_partitions: int = 1
    replication_factor: int = 1
    configs: Optional[Dict[str, Any]] = None

class KafkaTopicCreateResponse(BaseModel):
    success: bool
    message: Optional[str] = None