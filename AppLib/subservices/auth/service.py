"""
Authentication subservice using Keycloak and existing SecretsManager.
"""

from keycloak import KeycloakOpenID
from jose import JWTError
from fastapi import HTTPException, status
from typing import Dict, Any, Optional

class AuthService:
    def __init__(self, secrets_manager, keycloak_config: Dict[str, Any]):
        """
        Args:
            secrets_manager: Instance of AppLib.services.secrets.manager.SecretsManager
            keycloak_config: From main config (server_url, client_id, realm, vault_secret_path)
        """
        self.secrets_manager = secrets_manager
        self.keycloak_config = keycloak_config
        self.keycloak_openid: Optional[KeycloakOpenID] = None

    async def initialize(self):
        """Async initialization to fetch required secrets"""
        # Get Keycloak client secret from Vault via SecretsManager
        client_secret = await self.secrets_manager.fetch_secret(
            f"{self.keycloak_config['vault_secret_path']}/client_secret"
        )
        
        # Initialize Keycloak client
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.keycloak_config["server_url"],
            client_id=self.keycloak_config["client_id"],
            realm_name=self.keycloak_config["realm"],
            client_secret_key=client_secret,
            verify=True
        )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT using Keycloak's public key"""
        if not self.keycloak_openid:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth service not initialized"
            )

        try:
            public_key = (
                "-----BEGIN PUBLIC KEY-----\n"
                + self.keycloak_openid.public_key()
                + "\n-----END PUBLIC KEY-----"
            )
            return self.keycloak_openid.decode_token(
                token,
                key=public_key,
                options={"verify_signature": True, "verify_aud": False, "exp": True}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
