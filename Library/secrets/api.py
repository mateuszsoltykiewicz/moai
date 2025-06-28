from fastapi import APIRouter, HTTPException, Body, Depends, Request
from .manager import SecretsManager
from .schemas import SecretResponse, SecretUpdateRequest
from .exceptions import SecretNotFoundError, SecretValidationError, SecretPermissionError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/secrets", tags=["secrets"])
secrets_manager: SecretsManager = None

@router.get("/{path:path}", response_model=SecretResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "secrets", "read"))])
async def get_secret(request: Request, path: str):
    try:
        return await secrets_manager.get(path)
    except SecretNotFoundError as e:
        logger.warning(f"Secret not found: {path}")
        raise HTTPException(404, str(e))
    except SecretPermissionError as e:
        logger.warning(f"Permission denied for secret: {path}")
        raise HTTPException(403, str(e))

@router.patch("/{path:path}", response_model=SecretResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "secrets", "write"))])
async def update_secret(request: Request, path: str, req: SecretUpdateRequest = Body(...)):
    try:
        return await secrets_manager.set(path, req.value, version=req.version)
    except SecretValidationError as e:
        logger.warning(f"Secret validation failed for {path}: {e}")
        raise HTTPException(422, str(e))
    except SecretPermissionError as e:
        logger.warning(f"Permission denied for secret update: {path}")
        raise HTTPException(403, str(e))
