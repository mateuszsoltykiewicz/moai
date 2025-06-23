from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class S3Config(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    region: Optional[str] = None
    bucket: str

class S3ObjectInfo(BaseModel):
    key: str
    size: int
    last_modified: Optional[datetime]
    etag: Optional[str]
