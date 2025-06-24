from pydantic import BaseModel, Field
from typing import Optional, Dict

class VaultConfig(BaseModel):
    address: str
    token: str
    secrets_path: str
    verify_ssl: bool = True
    fallback_json: Optional[str] = None

class SecretEntry(BaseModel):
    key: str
    value: str
    metadata: Optional[Dict[str, Any]] = None
