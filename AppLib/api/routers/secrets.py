from fastapi import APIRouter, Depends, status
from typing import Optional
from models.schemas import (
    SecretCreateRequest, SecretUpdateRequest,
    SecretResponse, SecretRetrieveResponse
)
from api.dependencies import get_current_user
from api.main import APIException
from adapters.vault import AsyncVaultAdapter
from metrics.secrets import (
    SECRETS_CREATED, SECRETS_RETRIEVED, SECRETS_UPDATED, SECRETS_DELETED, SECRETS_ERRORS
)

router = APIRouter(tags=["secrets"])
BACKEND = "vault"

def get_vault_adapter():
    return AsyncVaultAdapter()

@router.post(
    "/",
    response_model=SecretResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new secret"
)
async def create_secret(
    req: SecretCreateRequest,
    user=Depends(get_current_user),
    vault: AsyncVaultAdapter = Depends(get_vault_adapter)
):
    try:
        existing = await vault.get_secret(req.name)
        if existing:
            SECRETS_ERRORS.labels(backend=BACKEND, operation="create").inc()
            raise APIException(
                status_code=status.HTTP_409_CONFLICT,
                message="Secret with this name already exists."
            )
        await vault.set_secret(req.name, {"value": req.value, "description": req.description})
        SECRETS_CREATED.labels(backend=BACKEND).inc()
        return SecretResponse(name=req.name, description=req.description)
    except Exception as e:
        SECRETS_ERRORS.labels(backend=BACKEND, operation="create").inc()
        raise

@router.get(
    "/{name}",
    response_model=SecretRetrieveResponse,
    summary="Retrieve a secret"
)
async def get_secret(
    name: str,
    user=Depends(get_current_user),
    vault: AsyncVaultAdapter = Depends(get_vault_adapter)
):
    try:
        secret = await vault.get_secret(name)
        if not secret:
            SECRETS_ERRORS.labels(backend=BACKEND, operation="retrieve").inc()
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Secret not found."
            )
        SECRETS_RETRIEVED.labels(backend=BACKEND).inc()
        return SecretRetrieveResponse(name=name, value=secret["value"], description=secret.get("description"))
    except Exception as e:
        SECRETS_ERRORS.labels(backend=BACKEND, operation="retrieve").inc()
        raise

@router.put(
    "/{name}",
    response_model=SecretResponse,
    summary="Update a secret"
)
async def update_secret(
    name: str,
    req: SecretUpdateRequest,
    user=Depends(get_current_user),
    vault: AsyncVaultAdapter = Depends(get_vault_adapter)
):
    try:
        secret = await vault.get_secret(name)
        if not secret:
            SECRETS_ERRORS.labels(backend=BACKEND, operation="update").inc()
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Secret not found."
            )
        await vault.set_secret(name, {"value": req.value, "description": req.description})
        SECRETS_UPDATED.labels(backend=BACKEND).inc()
        return SecretResponse(name=name, description=req.description)
    except Exception as e:
        SECRETS_ERRORS.labels(backend=BACKEND, operation="update").inc()
        raise

@router.delete(
    "/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a secret"
)
async def delete_secret(
    name: str,
    user=Depends(get_current_user),
    vault: AsyncVaultAdapter = Depends(get_vault_adapter)
):
    try:
        secret = await vault.get_secret(name)
        if not secret:
            SECRETS_ERRORS.labels(backend=BACKEND, operation="delete").inc()
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Secret not found."
            )
        await vault.delete_secret(name)
        SECRETS_DELETED.labels(backend=BACKEND).inc()
    except Exception as e:
        SECRETS_ERRORS.labels(backend=BACKEND, operation="delete").inc()
        raise
