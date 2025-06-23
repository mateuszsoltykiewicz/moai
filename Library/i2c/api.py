"""
API endpoints for I2CManager.

- Exposes /i2c/control, /i2c/status, /i2c/devices endpoints
"""

from fastapi import APIRouter, HTTPException, Body, Query
from .manager import I2CManager
from .schemas import I2CControlRequest, I2CStatusResponse

router = APIRouter(prefix="/i2c", tags=["i2c"])

# i2c_manager should be initialized with config at app startup
i2c_manager: I2CManager = None

@router.post("/control", response_model=I2CStatusResponse)
async def control_device(req: I2CControlRequest = Body(...)):
    """
    Control a relay, valve, or pump via GPIO.
    """
    try:
        return await i2c_manager.control(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", response_model=I2CStatusResponse)
async def get_status(device: str = Query(...)):
    """
    Get the status of a relay or I2C device.
    """
    try:
        return await i2c_manager.get_status(device)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/devices", response_model=list[str])
async def list_devices():
    """
    List all known relay and I2C device names.
    """
    return await i2c_manager.list_devices()
