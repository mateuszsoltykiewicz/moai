from fastapi import APIRouter, Depends, status, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.schemas import (
    CANBusStreamConfigRequest,
    CANBusStreamConfigResponse,
    CANBusStatusResponse
)
from api.dependencies import get_current_user
from api.main import APIException
from subservices.canbus.canbus_adapter import CANBusAdapter

router = APIRouter(tags=["canbus"])

# Store adapters by ID (in production, use a registry or DB)
CANBUS_ADAPTERS: Dict[str, CANBusAdapter] = {}

@router.post(
    "/stream/configure",
    response_model=CANBusStreamConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Configure CANBus streaming"
)
async def configure_canbus_stream(
    config: CANBusStreamConfigRequest,
    user=Depends(get_current_user)
):
    """
    Configure a CANBus adapter for data streaming.
    """
    try:
        adapter = CANBusAdapter(channel=config.adapter_id, bitrate=config.bitrate)
        await adapter.configure(filters=config.filters)
        CANBUS_ADAPTERS[config.adapter_id] = adapter
        return CANBusStreamConfigResponse(success=True, message="CANBus stream configured.")
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to configure CANBus stream.",
            details={"error": str(e)}
        )

@router.get(
    "/status/{adapter_id}",
    response_model=CANBusStatusResponse,
    summary="Get CANBus adapter status"
)
async def get_canbus_status(
    adapter_id: str,
    user=Depends(get_current_user)
):
    """
    Get the current status of a CANBus adapter.
    """
    adapter = CANBUS_ADAPTERS.get(adapter_id)
    if not adapter:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"CANBus adapter '{adapter_id}' not found.",
            details={"adapter_id": adapter_id}
        )
    return CANBusStatusResponse(
        adapter_id=adapter_id,
        status="streaming" if adapter._streaming else "stopped",
        last_configured=datetime.utcnow().isoformat()
    )

@router.get(
    "/stream/{adapter_id}",
    response_model=List[Dict[str, Any]],
    summary="Stream CANBus messages"
)
async def stream_canbus_messages(
    adapter_id: str,
    max_messages: int = 100,
    user=Depends(get_current_user)
):
    """
    Stream CANBus messages from the adapter.
    """
    adapter = CANBUS_ADAPTERS.get(adapter_id)
    if not adapter or not adapter._streaming:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"CANBus adapter '{adapter_id}' not streaming.",
            details={"adapter_id": adapter_id}
        )
    messages = []
    async for msg in adapter.read_stream(max_messages=max_messages):
        messages.append(msg)
    return messages
