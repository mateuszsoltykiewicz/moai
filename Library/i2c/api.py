from fastapi import APIRouter, HTTPException, Body, Query
from .manager import I2CManager
from .schemas import I2CControlRequest, I2CStatusResponse
from .exceptions import I2CError, I2CDeviceNotFoundError, I2CInvalidActionError

router = APIRouter(prefix="/i2c", tags=["i2c"])
i2c_manager: I2CManager = None

@router.post("/control", response_model=I2CStatusResponse)
async def control_device(req: I2CControlRequest = Body(...)):
    try:
        return await i2c_manager.control(req)
    except I2CDeviceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except I2CInvalidActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except I2CError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/status", response_model=I2CStatusResponse)
async def get_status(device: str = Query(...)):
    try:
        return await i2c_manager.get_status(device)
    except I2CDeviceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except I2CError as e:
        raise HTTPException(status_code=503, detail=str(e))

# ... (other endpoints with similar error handling) ...
