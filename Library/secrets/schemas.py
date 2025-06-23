"""
Pydantic schemas for SecretsManager.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SecretUpdateRequest(BaseModel):
    path: str = Field(..., example="service/api-key")
    value: Dict[str, Any] = Field(..., example={"key": "new-secret-value"})
    version: Optional[int] = Field(None, description="Version for concurrency")

class SecretResponse(BaseModel):
    path: str
    value: Dict[str, Any]
    version: int
    updated: bool = False
    message: Optional[str] = None
