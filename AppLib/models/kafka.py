from pydantic import BaseModel, Field, SecretStr
from typing import Optional

class KafkaConfig(BaseModel):
    bootstrap_servers: str = Field(..., description="Kafka bootstrap servers")
    group_id: str = Field(..., description="Kafka consumer group ID")
    auto_offset_reset: str = Field(default="earliest", description="Kafka offset reset policy")
    security_protocol: Optional[str] = Field(default="PLAINTEXT")
    ssl_cafile: Optional[str]
    ssl_certfile: Optional[str]
    ssl_keyfile: Optional[str]