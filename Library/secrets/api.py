from fastapi import APIRouter, HTTPException, status, Body, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import SecretsManager
from .schemas import SecretResponse, SecretUpdateRequest
from .exceptions import SecretNotFoundError, SecretValidationError, SecretPermissionError

API_KEY_NAME = "X-SECRETS-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # Replace with Vault or secrets manager validation
    if not api_key or api_key != "SECURE_API_KEY": 
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/secrets", tags=["secrets"])
secrets_manager: SecretsManager = None

@router.get("/{path:path}", response_model=SecretResponse, dependencies=[Depends(validate_api_key)])
async def get_secret(path: str):
    try:
        return await secrets_manager.get(path)
    except SecretNotFoundError as e:
        raise HTTPException(404, str(e))
    except SecretPermissionError as e:
        raise HTTPException(403, str(e))

@router.patch("/{path:path}", response_model=SecretResponse, dependencies=[Depends(validate_api_key)])
async def update_secret(path: str, req: SecretUpdateRequest = Body(...)):
    try:
        return await secrets_manager.set(path, req.value, version=req.version)
    except SecretValidationError as e:
        raise HTTPException(422, str(e))
    except SecretPermissionError as e:
        raise HTTPException(403, str(e))
