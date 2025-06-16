from pydantic import BaseModel, Field
from typing import Optional

class KeycloakConfig(BaseModel):
    server_url: str
    client_id: str
    realm: str
    vault_secret_path: str = "keycloak"