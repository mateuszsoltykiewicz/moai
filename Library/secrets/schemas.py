from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SecretUpdateRequest(BaseModel):
    value: Dict[str, Any] = Field(..., example={"api_key": "new-value"})
    version: Optional[int] = Field(None, description="CAS version for concurrency control")

class SecretResponse(BaseModel):
    path: str
    value: Dict[str, Any]
    version: int
    updated: bool = False
    metadata: Optional[Dict[str, Any]] = None  # Vault metadata
    error: Optional[str] = None
