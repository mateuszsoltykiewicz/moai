# Library/api/security.py
from fastapi import Request, HTTPException, Depends
from Library.auth.manager import AuthManager
from Library.secrets.manager import SecretsManager

# Configure these globally or inject as needed
KEYCLOAK_ISSUER = "https://keycloak.example.com/realms/yourrealm"
RBAC_POLICY_PATH = "rbac/policies"
secrets_manager = SecretsManager()
auth_manager = AuthManager(KEYCLOAK_ISSUER, secrets_manager, RBAC_POLICY_PATH)

async def require_jwt_and_rbac(request: Request, resource: str = "default", action: str = "read"):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        context = auth_manager.validate_token(token)
        if not auth_manager.check_permission(context, resource, action):
            raise HTTPException(status_code=403, detail="Permission denied")
        return context
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
