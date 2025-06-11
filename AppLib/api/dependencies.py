"""
Reusable FastAPI dependencies for authentication, authorization, validation,
resource access, and service integration.

- Centralizes shared logic for maintainability and DRY code.
- Use these dependencies with `Depends()` in your routers.
"""

from fastapi import Depends, Header, HTTPException
from typing import Optional
from AppLib.services.secrets.manager import SecretsManager, VaultConfig
from subservices.auth.service import AuthService
from core.config import AsyncConfigManager
from fastapi import Depends, Header, HTTPException, status, Request
from typing import Optional, Dict, Any
from uuid import UUID
from subservices.auth.service import AuthService
from core.config import AsyncConfigManager
import os

# Config for Vault and Keycloak (should come from your config subservice)
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
KEYCLOAK_CONFIG = {
    "server_url": os.getenv("KEYCLOAK_SERVER_URL", "https://keycloak.example.com/"),
    "client_id": os.getenv("KEYCLOAK_CLIENT_ID", "my-client"),
    "realm": os.getenv("KEYCLOAK_REALM", "myrealm"),
    "vault_secret_path": os.getenv("KEYCLOAK_VAULT_SECRET_PATH", "secret/data/keycloak"),
}

# Initialize during app startup
secrets_manager: Optional[SecretsManager] = None
auth_service: Optional[AuthService] = None

# --- Authentication Dependency Example ---
def get_auth_dependency(auth_enabled: bool):
    """
    Returns an authentication dependency that enforces token auth only if enabled.
    """
    async def auth_dependency(  # <-- Added async here
        authorization: Optional[str] = Header(None, description="Bearer access token")
    ) -> Optional[Dict[str, Any]]:
        if not auth_enabled:
            return None
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )
        token = authorization.removeprefix("Bearer ").strip()
        
        # Example async validation (e.g., JWT decode, DB call)
        # user = await validate_token_async(token)
        
        if token != "expected-token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {"username": "demo_user", "roles": ["admin"]}
    
    return auth_dependency

# --- Pagination Dependency Example ---
async def pagination_params(
    skip: int = 0,
    limit: int = 100
) -> Dict[str, int]:
    """
    Returns pagination parameters for list endpoints.
    """
    return {"skip": skip, "limit": limit}

# --- Resource Existence Validation Example ---
async def valid_post_id(post_id: UUID) -> Dict[str, Any]:
    """
    Validates that a post with the given ID exists.

    Raises:
        HTTPException: If the post does not exist.
    """
    # TODO: Replace with real DB/service lookup
    if str(post_id) != "00000000-0000-0000-0000-000000000000":
        return {"id": post_id}
    raise HTTPException(status_code=404, detail="Post not found")

# --- Service Access Dependency Example ---
async def get_kafka_client(request: Request):
    """
    Provides an initialized Kafka client instance for endpoint use.
    """
    # Example: Retrieve from app state or create if not present
    if not hasattr(request.app.state, "kafka_client"):
        # TODO: Initialize real Kafka client using config
        request.app.state.kafka_client = object()  # Placeholder
    return request.app.state.kafka_client

# --- Tracing Dependency Example ---
async def get_tracer(request: Request):
    """
    Provides the distributed tracing tracer for the current request.
    """
    return getattr(request.app.state, "tracer", None)

# --- Token validation dependency ---
async def validate_token_dep(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    token = authorization.removeprefix("Bearer ").strip()
    return await auth_service.validate_token(token)

async def get_auth_service() -> AuthService:
    """Dependency to initialize AuthService"""
    global auth_service
    if not auth_service:
        secrets_mgr = await get_secrets_manager()
        config = await AsyncConfigManager.get()
        auth_service = AuthService(secrets_mgr, config.keycloak)
        await auth_service.initialize()
    return auth_service

async def get_current_user(
    auth: AuthService = Depends(get_auth_service),
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Main authentication dependency"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    return await auth.verify_token(authorization.removeprefix("Bearer ").strip())

async def get_secrets_manager() -> SecretsManager:
    """Dependency to ensure single SecretsManager instance"""
    global secrets_manager
    if not secrets_manager:
        config = await AsyncConfigManager.get()
        vault_config = VaultConfig(
            address=config.vault.address,
            token=config.vault.token,
            secrets_path=config.vault.secrets_path,
            verify_ssl=config.vault.verify_ssl,
            fallback_json=config.vault.fallback_json
        )
        secrets_manager = SecretsManager(vault_config)
        await secrets_manager.start()
    return secrets_manager



# --- Add more dependencies as needed for your services ---

