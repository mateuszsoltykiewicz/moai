from pydantic import BaseModel, Field
from typing import Optional

class OAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    issuer: str
    jwks_uri: str
    audience: str
    userinfo_endpoint: Optional[str] = None

class KeycloakConfig(BaseModel):
    server_url: str
    client_id: str
    realm: str
    vault_secret_path: str = "keycloak"
