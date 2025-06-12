"""
Config API Router

- Allows secure retrieval and update of application configuration.
- Integrates with the async config subservice.
- All endpoints require authentication.
- Ready for hot reload and audit integration.
"""

from fastapi import APIRouter, Depends, status, Request
from models.schemas import ConfigResponseSchema, ConfigUpdateRequest
from api.dependencies import get_current_user
from api.main import APIException
from core.config import AsyncConfigManager
from models.config import AppConfig

router = APIRouter(tags=["config"])

@router.get(
    "/",
    response_model=ConfigResponseSchema,
    summary="Get current configuration",
    description="Retrieve the current application configuration."
)
async def get_config(
    request: Request,
    user=Depends(get_current_user)
):
    """
    Return the current application configuration.
    """
    config_mgr: AsyncConfigManager = request.app.state.config_mgr
    config: AppConfig = await config_mgr.get()
    # Optionally, filter sensitive fields before returning
    return ConfigResponseSchema(config=config.model_dump())

@router.post(
    "/",
    response_model=ConfigResponseSchema,
    summary="Update configuration",
    description="Update the application configuration. Triggers hot reload."
)
async def update_config(
    req: ConfigUpdateRequest,
    request: Request,
    user=Depends(get_current_user)
):
    """
    Update the application configuration and trigger hot reload.
    """
    config_mgr: AsyncConfigManager = request.app.state.config_mgr

    # Optionally, add RBAC here to restrict who can update config
    # Example: require_roles(["admin"])(user)

    try:
        # Validate and apply new config
        new_config = AppConfig.model_validate(req.config)
        await config_mgr.set(new_config)
        # Optionally, log/audit the update with req.reason and user info
        return ConfigResponseSchema(config=new_config.model_dump())
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid configuration update.",
            details={"error": str(e)}
        )
