from pydantic import BaseModel, Field
from typing import Optional

class VaultConfig(BaseModel):
    address: str
    token: str
    secrets_path: str
    verify_ssl: bool = True
    fallback_json: Optional[str] = None