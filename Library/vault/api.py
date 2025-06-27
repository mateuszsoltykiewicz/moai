from fastapi import APIRouter, HTTPException, Body, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import VaultManager
from .schemas import VaultSecretResponse, VaultTokenResponse
from .exceptions import VaultError, VaultNotFoundError, VaultPermissionError

API_KEY_NAME = "X-VAULT-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # Validate against Vault or secrets manager
    if not api_key or api_key != "SECURE_API_KEY":
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/vault", tags=["vault"])
vault_manager: VaultManager = None

@router.get("/secrets/{path:path}", response_model=VaultSecretResponse, dependencies=[Depends(validate_api_key)])
async def get_secret(path: str):
    try:
        data, version = await vault_manager.read_secret(path)
        return {"path": path, "data": data, "version": version}
    except VaultNotFoundError as e:
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")

@router.put("/secrets/{path:path}", response_model=VaultSecretResponse, dependencies=[Depends(validate_api_key)])
async def set_secret(path: str, data: Dict[str, Any] = Body(...)):
    try:
        version = await vault_manager.write_secret(path, data)
        # Read after write to ensure consistency
        new_data, _ = await vault_manager.read_secret(path)
        return {"path": path, "data": new_data, "version": version}
    except VaultNotFoundError as e:
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")

@router.delete("/secrets/{path:path}", status_code=204, dependencies=[Depends(validate_api_key)])
async def delete_secret(path: str):
    try:
        await vault_manager.delete_secret(path)
    except VaultNotFoundError as e:
        raise HTTPException(404, str(e))
    except VaultPermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")

@router.post("/token/renew", response_model=VaultTokenResponse, dependencies=[Depends(validate_api_key)])
async def renew_token():
    try:
        return await vault_manager.renew_token()
    except Exception as e:
        raise HTTPException(500, f"Internal error: {str(e)}")
