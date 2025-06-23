"""
API endpoints for VaultManager.

- Exposes /vault/secrets/{path} for CRUD operations
- Exposes /vault/token/renew for token renewal
"""

from fastapi import APIRouter, HTTPException, status, Body
from .manager import VaultManager
from .schemas import VaultSecretResponse, VaultTokenResponse
from .exceptions import VaultError, VaultNotFoundError
from typing import Any, Dict

router = APIRouter(prefix="/vault", tags=["vault"])

# vault_manager should be initialized with Vault config at app startup
vault_manager: VaultManager = None

@router.get("/secrets/{path:path}", response_model=VaultSecretResponse)
async def get_secret(path: str):
    """
    Retrieve a secret from Vault.
    """
    try:
        data, version = await vault_manager.read_secret(path)
        return {"path": path, "data": data, "version": version}
    except VaultNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VaultError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.put("/secrets/{path:path}", response_model=VaultSecretResponse)
async def set_secret(path: str,  data: Dict[str, Any] = Body(...)):
    """
    Write a secret to Vault.
    """
    try:
        version = await vault_manager.write_secret(path, data)
        new_data, _ = await vault_manager.read_secret(path)
        return {"path": path, "data": new_data, "version": version}
    except VaultError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.delete("/secrets/{path:path}", status_code=204)
async def delete_secret(path: str):
    """
    Delete a secret from Vault.
    """
    try:
        await vault_manager.delete_secret(path)
    except VaultError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/token/renew", response_model=VaultTokenResponse)
async def renew_token():
    """
    Renew Vault token.
    """
    try:
        await vault_manager.renew_token()
        # In real usage, you'd return the new token details if available
        return {"token": "renewed", "renewable": True, "ttl": 3600}
    except VaultError as e:
        raise HTTPException(status_code=503, detail=str(e))
