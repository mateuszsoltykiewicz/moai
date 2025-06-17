from pydantic import BaseModel, Field, SecretStr
from typing import Optional

class SecretCreateRequest(BaseModel):
    name: str = Field(..., description="Secret name (unique key)")
    value: SecretStr = Field(..., description="Secret value (will be stored securely)")
    description: Optional[str] = Field(None, description="Optional description")

    class Config:
        schema_extra = {
            "example": {
                "name": "db_password",
                "value": "s3cr3t!",
                "description": "Database password for prod"
            }
        }

class SecretUpdateRequest(BaseModel):
    value: SecretStr = Field(..., description="New secret value")
    description: Optional[str] = Field(None, description="Optional description")

    class Config:
        schema_extra = {
            "example": {
                "value": "n3wp@ssw0rd",
                "description": "Rotated password"
            }
        }

class SecretResponse(BaseModel):
    name: str = Field(..., description="Secret name")
    description: Optional[str] = Field(None, description="Optional description")

    class Config:
        schema_extra = {
            "example": {
                "name": "db_password",
                "description": "Database password for prod"
            }
        }

class SecretRetrieveResponse(BaseModel):
    name: str = Field(..., description="Secret name")
    value: SecretStr = Field(..., description="Secret value (will be stored securely)")
    description: Optional[str] = Field(None, description="Optional description")

    class Config:
        schema_extra = {
            "example": {
                "name": "db_password",
                "value": "s3cr3t!",
                "description": "Database password for prod"
            }
        }
