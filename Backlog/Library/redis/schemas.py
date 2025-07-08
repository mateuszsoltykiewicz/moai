from pydantic import BaseModel, Field
from typing import Optional

class RedisStatusResponse(BaseModel):
    status: str

class RedisKVRequest(BaseModel):
    key: str = Field(..., example="mykey")
    value: str = Field(..., example="myvalue")
    expire: Optional[int] = Field(None, description="Expiration in seconds")
