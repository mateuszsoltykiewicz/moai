# api/routers/updates.py
from fastapi import APIRouter, Depends, HTTPException, status
from adapters.update import UpdateAdapter
from typing import Optional
from core.config import AsyncConfigManager
from core.state import AppState
from models.schemas import UpdateCheckResponse, UpdateTriggerResponse

router = APIRouter(tags=["updates"])

async def get_update_adapter(
    config: AsyncConfigManager = Depends(AsyncConfigManager.get_instance),
    state: AppState = Depends(AppState.get_instance)
) -> UpdateAdapter:
    return UpdateAdapter(config, state)

@router.get(
    "/check",
    response_model=UpdateCheckResponse,
    summary="Check for available updates"
)
async def check_for_updates(adapter: UpdateAdapter = Depends(get_update_adapter)):
    try:
        update_info = await adapter.check_for_updates()
        return UpdateCheckResponse(
            update_available=update_info["update_available"],
            current_version=update_info["current_version"],
            latest_version=update_info["latest_version"],
            details=update_info.get("release_notes", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@router.post(
    "/trigger",
    response_model=UpdateTriggerResponse,
    summary="Trigger system update"
)
async def trigger_update(
    version: Optional[str] = None,
    adapter: UpdateAdapter = Depends(get_update_adapter)
):
    try:
        result = await adapter.perform_update(version)
        return UpdateTriggerResponse(
            success=True,
            message=f"Successfully updated to version {result['new_version']}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
