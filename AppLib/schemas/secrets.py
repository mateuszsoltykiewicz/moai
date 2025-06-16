from pydantic import BaseModel, Field
from typing import Optional

class SecretCreateRequest(BaseModel):
    name: str = Field(..., description="Secret name (unique key)")
    value: str = Field(..., description="Secret value (will be stored securely)")
    description: Optional[str] = Field(None, description="Optional description")

class SecretUpdateRequest(BaseModel):
    value: str = Field(..., description="New secret value")
    description: Optional[str] = Field(None, description="Optional description")

class SecretResponse(BaseModel):
    name: str
    description: Optional[str] = None

class SecretRetrieveResponse(BaseModel):
    name: str
    value: str
    description: Optional[str] = None