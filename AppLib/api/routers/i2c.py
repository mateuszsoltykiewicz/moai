from fastapi import APIRouter, Depends, status, Request
from typing import Dict
from models.schemas import (
    I2CCommandConfigRequest,
    I2CCommandQueueRequest,
    I2CCommandResponse
)
from core.exceptions import I2CException
from adapters.i2c import I2CAdapter
from api.dependencies import get_current_user
from api.main import APIException

router = APIRouter(tags=["i2c"])

def get_adapter(request: Request, adapter_id: str) -> I2CAdapter:
    """Get or create I2C adapter from app state"""
    if not hasattr(request.app.state, "i2c_adapters"):
        request.app.state.i2c_adapters = {}
    
    adapters = request.app.state.i2c_adapters
    if adapter_id not in adapters:
        adapters[adapter_id] = I2CAdapter(adapter_id)
    return adapters[adapter_id]

@router.post(
    "/start/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="Start I2C adapter"
)
async def start_adapter(
    adapter_id: str,
    request: Request,
    user=Depends(get_current_user)
):
    try:
        adapter = get_adapter(request, adapter_id)
        await adapter.start()
        return I2CCommandResponse(
            success=True,
            message=f"I2C adapter {adapter_id} started",
            details={"status": "running"}
        )
    except I2CException as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

@router.post(
    "/stop/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="Stop I2C adapter"
)
async def stop_adapter(
    adapter_id: str,
    request: Request,
    user=Depends(get_current_user)
):
    try:
        adapter = get_adapter(request, adapter_id)
        await adapter.stop()
        return I2CCommandResponse(
            success=True,
            message=f"I2C adapter {adapter_id} stopped",
            details={"status": "stopped"}
        )
    except I2CError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

@router.get(
    "/health/{adapter_id}",
    response_model=I2CCommandResponse,
    summary="I2C adapter health check"
)
async def i2c_health_check(
    adapter_id: str,
    request: Request,
    user=Depends(get_current_user)
):
    adapter = get_adapter(request, adapter_id)
    healthy = await adapter.health_check()
    return I2CCommandResponse(
        success=healthy,
        message="Healthy" if healthy else "Unhealthy",
        details={"status": "healthy" if healthy else "unhealthy"}
    )

# Existing configure and queue endpoints with Request injection
@router.post(
    "/command/configure",
    response_model=I2CCommandResponse,
    status_code=status.HTTP_200_OK,
    summary="Configure I2C GPIO pin"
)
async def configure_i2c_command(
    config: I2CCommandConfigRequest,
    request: Request,
    user=Depends(get_current_user)
):
    try:
        adapter = get_adapter(request, config.adapter_id)
        await adapter.configure_gpio(
            gpio_pin=config.gpio_pin,
            mode=config.mode,
            initial_state=config.initial_state
        )
        return I2CCommandResponse(success=True, message="I2C GPIO configured")
    except I2CError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )

@router.post(
    "/command/queue",
    response_model=I2CCommandResponse,
    status_code=status.HTTP_200_OK,
    summary="Queue I2C commands"
)
async def queue_i2c_commands(
    request_data: I2CCommandQueueRequest,
    request: Request,
    user=Depends(get_current_user)
):
    try:
        adapter = get_adapter(request, request_data.adapter_id)
        await adapter.queue_commands(request_data.commands)
        return I2CCommandResponse(success=True, message="Commands queued")
    except I2CError as e:
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )
