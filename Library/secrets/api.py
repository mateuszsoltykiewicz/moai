"""
API endpoints for SecretsManager.

- Exposes /secrets/{path} for get/set operations
"""

from fastapi import APIRouter, HTTPException, status, Body
from .manager import SecretsManager
from .schemas import SecretResponse, SecretUpdateRequest
from .exceptions import SecretNotFoundError, SecretValidationError

router = APIRouter(prefix="/secrets", tags=["secrets"])

# secrets_manager should be initialized with a VaultManager instance at app startup
secrets_manager: SecretsManager = None

@router.get("/{path:path}", response_model=SecretResponse)
async def get_secret(path: str):
    """
    Retrieve a secret.
    """
    try:
        return await secrets_manager.get(path)
    except SecretNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{path:path}", response_model=SecretResponse)
async def update_secret(path: str, req: SecretUpdateRequest = Body(...)):
    """
    Update or rotate a secret.
    """
    try:
        return await secrets_manager.set(path, req.value, version=req.version)
    except SecretValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
