from pydantic import BaseModel
from typing import Dict, Any

class VaultSecretResponse(BaseModel):
    path: str
    data: Dict[str, Any]
    version: int

class VaultTokenResponse(BaseModel):
    token: str
    renewable: bool
    ttl: int
