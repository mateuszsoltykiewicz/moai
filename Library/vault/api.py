from fastapi import APIRouter, HTTPException, Body, Depends, Request
from typing import Dict, Any
from .manager import VaultManager
from .schemas import VaultSecretResponse, VaultTokenResponse
from .exceptions import VaultError, VaultNotFoundError, VaultPermissionError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/vault", tags=["vault"])
vault_manager: VaultManager = None

@router.get("/secrets/{path:path}", response_model=VaultSecretResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "vault", "read"))])
async def get_secret(request: Request, path: str):
    try:
        data, version = await vault_manager.read_secret(path)
        return {"path": path, "data": data, "version": version}
    except VaultNotFoundError as e:
        logger.warning(f"Secret not found: {path}")
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        logger.warning(f"Permission denied for secret: {path}")
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.error(f"Internal error in get_secret: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.put("/secrets/{path:path}", response_model=VaultSecretResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "vault", "write"))])
async def set_secret(request: Request, path: str, data: Dict[str, Any] = Body(...)):
    try:
        version = await vault_manager.write_secret(path, data)
        new_data, _ = await vault_manager.read_secret(path)
        return {"path": path, "data": new_data, "version": version}
    except VaultNotFoundError as e:
        logger.warning(f"Secret not found: {path}")
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        logger.warning(f"Permission denied for secret: {path}")
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.error(f"Internal error in set_secret: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.delete("/secrets/{path:path}", status_code=204, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "vault", "delete"))])
async def delete_secret(request: Request, path: str):
    try:
        await vault_manager.delete_secret(path)
    except VaultNotFoundError as e:
        logger.warning(f"Secret not found: {path}")
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        logger.warning(f"Permission denied for secret: {path}")
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.error(f"Internal error in delete_secret: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.post("/token/renew", response_model=VaultTokenResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "vault", "write"))])
async def renew_token(request: Request):
    try:
        return await vault_manager.renew_token()
    except Exception as e:
        logger.error(f"Internal error in renew_token: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
