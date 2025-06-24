"""
Secrets API Router

- Secure, RBAC-protected endpoints for secret rotation and retrieval
- Integrates with Vault via SecretsManager
- Pre/post hooks for auditing and validation
- Observability (tracing, metrics, logging)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from typing import Dict, Any
from schemas.secrets import SecretUpdateRequest, SecretResponse
from api.dependencies import base_endpoint_processor, require_role
from core.metrics import record_secrets_operation
from core.tracing import AsyncTracer
from core.logging import logger
from AppLib.services.secrets.manager import SecretsManager
import time

tracer = AsyncTracer("applib-secrets").get_tracer()

router = APIRouter(
    prefix="/secrets",
    tags=["secrets"],
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"}
    }
)

def get_secrets_manager() -> SecretsManager:
    # Should be initialized at app startup and injected via DI in production
    # For demo, instantiate here (not recommended for real prod)
    from core.config import AsyncConfigManager
    import asyncio
    config = asyncio.run(AsyncConfigManager("configs/app_config.json").get())
    return SecretsManager(config.vault)

@router.get(
    "/{path:path}",
    response_model=SecretResponse,
    summary="Retrieve secret"
)
async def get_secret(
    path: str,
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="secrets:get",
            dependencies=[Depends(require_role("secrets.read"))]
        )
    ),
    request: Request = None
):
    """
    Retrieve a secret from Vault.
    - RBAC via 'secrets.read'
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        with tracer.start_as_current_span("secrets_get"):
            secrets_manager = get_secrets_manager()
            secret, version = await secrets_manager.get_secret(path)
            response = SecretResponse(path=path, value=secret, version=version, updated=False)
        duration = time.monotonic() - start_time
        record_secrets_operation("get", duration)
        logger.info(f"Secret retrieved at {path} by {context['user'].sub} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Secret retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secret not found: {str(e)}"
        )

@router.patch(
    "/{path:path}",
    response_model=SecretResponse,
    summary="Update/rotate secret"
)
async def update_secret(
    path: str,
    req: SecretUpdateRequest = Body(...),
    context: Dict[str, Any] = Depends(
        lambda r: base_endpoint_processor(
            r,
            endpoint_path="secrets:update",
            pre_hook="api.hooks.secrets.before_update",
            post_hook="api.hooks.secrets.after_update",
            dependencies=[Depends(require_role("secrets.update"))]
        )
    ),
    request: Request = None
):
    """
    Update or rotate a secret in Vault.
    - RBAC via 'secrets.update'
    - Pre/post hooks for validation/audit
    - Metrics and tracing
    """
    start_time = time.monotonic()
    try:
        # Pre-hook validation
        if "validation_result" in context and not context["validation_result"].get("valid", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=context["validation_result"].get("message", "Validation failed")
            )
        with tracer.start_as_current_span("secrets_update"):
            secrets_manager = get_secrets_manager()
            updated_version = await secrets_manager.set_secret(path, req.value, version=req.version)
            response = SecretResponse(path=path, value=req.value, version=updated_version, updated=True, message="Secret updated")
        duration = time.monotonic() - start_time
        record_secrets_operation("update", duration)
        logger.info(f"Secret updated at {path} by {context['user'].sub} in {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Secret update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update secret: {str(e)}"
        )
