import jwt
import requests
from typing import Dict, Any, Optional, List
from .exceptions import AuthError, AuthZError
from .schemas import AuthContext
from Library.logging import get_logger
from Library.secrets.manager import SecretsManager  # For fetching JWKS, RBAC policies

logger = get_logger(__name__)

class AuthManager:
    def __init__(self, keycloak_issuer: str, secrets_manager: SecretsManager, rbac_policy_path: str):
        self.issuer = keycloak_issuer
        self.secrets_manager = secrets_manager
        self.rbac_policy_path = rbac_policy_path
        self.jwks = None

    def _get_jwks(self):
        if self.jwks is None:
            # Fetch JWKS from Keycloak or Vault
            jwks_uri = f"{self.issuer}/protocol/openid-connect/certs"
            try:
                response = requests.get(jwks_uri)
                response.raise_for_status()
                self.jwks = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}", exc_info=True)
                raise AuthError("JWKS fetch failed") from e
        return self.jwks

    def validate_token(self, token: str) -> AuthContext:
        try:
            jwks = self._get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            key = next((k for k in jwks['keys'] if k['kid'] == unverified_header['kid']), None)
            if not key:
                logger.warning("No matching JWKS key found")
                raise AuthError("No matching JWKS key found")
                
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            payload = jwt.decode(
                token, 
                public_key, 
                algorithms=['RS256'], 
                audience='account', 
                issuer=self.issuer
            )
            
            logger.info(f"Token validated for subject: {payload.get('sub')}")
            return AuthContext(
                subject=payload.get('sub'),
                roles=payload.get('realm_access', {}).get('roles', []),
                claims=payload
            )
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=True)
            raise AuthError("Invalid or expired token") from e

    def check_permission(self, context: AuthContext, resource: str, action: str) -> bool:
        try:
            policy = self.secrets_manager.get(self.rbac_policy_path)
            allowed_roles = policy.get(resource, {}).get(action, [])
            
            if any(role in context.roles for role in allowed_roles):
                logger.info(f"Authorization granted for {context.subject} on {resource}:{action}")
                return True
                
            logger.warning(f"Authorization denied for {context.subject} on {resource}:{action}")
            raise AuthZError("Permission denied")
        except Exception as e:
            logger.error(f"RBAC check failed: {e}", exc_info=True)
            raise AuthZError("RBAC policy error") from e
