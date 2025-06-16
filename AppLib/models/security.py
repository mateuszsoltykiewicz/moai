from pydantic import BaseModel, Field
from typing import Optional

class VaultConfig(BaseModel):
    address: str
    token: str
    secrets_path: str
    verify_ssl: bool = True
    fallback_json: Optional[str] = None

class KeycloakConfig(BaseModel):
    server_url: str
    client_id: str
    realm: str
    vault_secret_path: str = "keycloak"

class AuthConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable token authentication for API routers")