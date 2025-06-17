from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class OffsetReset(str, Enum):
    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"

class KafkaProduceRequest(BaseModel):
    topic: str = Field(..., description="Kafka topic")
    key: Optional[str] = Field(None, description="Message key")
    value: Dict[str, Any] = Field(..., description="Message payload")
    partition: Optional[int] = Field(None, ge=0, description="Partition (optional, non-negative)")

    class Config:
        schema_extra = {
            "example": {
                "topic": "sensor.data",
                "key": "sensor-123",
                "value": {"temperature": 22.5, "unit": "C"},
                "partition": 0
            }
        }

class KafkaProduceResponse(BaseModel):
    success: bool = Field(..., description="Was the message produced successfully?")
    message: Optional[str] = Field(None, description="Additional information or errors")
    offset: Optional[int] = Field(None, description="Message offset in the topic")
    partition: Optional[int] = Field(None, description="Partition number")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Message produced successfully",
                "offset": 123,
                "partition": 0
            }
        }

class KafkaMessage(BaseModel):
    topic: str = Field(..., description="Kafka topic")
    key: Optional[str] = Field(None, description="Message key")
    value: Dict[str, Any] = Field(..., description="Message payload")
    offset: Optional[int] = Field(None, description="Message offset")
    partition: Optional[int] = Field(None, description="Partition number")
    timestamp: Optional[int] = Field(None, description="Epoch ms timestamp")

    class Config:
        schema_extra = {
            "example": {
                "topic": "sensor.data",
                "key": "sensor-123",
                "value": {"temperature": 22.5, "unit": "C"},
                "offset": 123,
                "partition": 0,
                "timestamp": 1728850123456
            }
        }

class KafkaConsumeRequest(BaseModel):
    topic: str = Field(..., description="Kafka topic to consume from")
    group_id: Optional[str] = Field(None, description="Consumer group ID")
    partition: Optional[int] = Field(None, ge=0, description="Partition number (optional)")
    offset: Optional[int] = Field(None, ge=0, description="Offset to start from (optional)")
    limit: int = Field(10, ge=1, le=1000, description="Max messages to fetch (default 10, max 1000)")
    auto_commit: bool = Field(True, description="Whether to auto-commit offsets")
    offset_reset: OffsetReset = Field(OffsetReset.LATEST, description="Where to start if no offset is present")

    class Config:
        schema_extra = {
            "example": {
                "topic": "sensor.data",
                "group_id": "data-processor",
                "partition": 0,
                "offset": 0,
                "limit": 5,
                "auto_commit": True,
                "offset_reset": "earliest"
            }
        }

class KafkaConsumeResponse(BaseModel):
    messages: List[KafkaMessage] = Field(..., description="List of consumed messages")

class KafkaTopicCreateRequest(BaseModel):
    topic: str = Field(..., description="Kafka topic name")
    num_partitions: int = Field(1, ge=1, le=1000, description="Number of partitions")
    replication_factor: int = Field(1, ge=1, le=10, description="Replication factor")
    configs: Optional[Dict[str, Any]] = Field(
        None, description="Optional topic-level configuration"
    )

    class Config:
        schema_extra = {
            "example": {
                "topic": "alerts.critical",
                "num_partitions": 3,
                "replication_factor": 2,
                "configs": {"retention.ms": 86400000}
            }
        }

class KafkaTopicCreateResponse(BaseModel):
    success: bool = Field(..., description="Was the topic created successfully?")
    topic: Optional[str] = Field(None, description="Topic name")
    message: Optional[str] = Field(None, description="Additional information or errors")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "topic": "alerts.critical",
                "message": "Topic created"
            }
        }
