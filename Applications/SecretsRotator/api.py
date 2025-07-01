from fastapi import APIRouter, Depends, HTTPException, Request
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import SecretsRotatorManager
from .schemas import SecretRotateRequest, SecretRotateResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/secrets", tags=["secrets"])

@router.post("/rotate", response_model=SecretRotateResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "secrets", "write"))])
async def rotate_secret(request: Request, req: SecretRotateRequest):
    try:
        result = await SecretsRotatorManager.rotate_secret(req)
        return result
    except Exception as e:
        logger.error(f"Secret rotation failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
