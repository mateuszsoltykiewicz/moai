from fastapi import APIRouter, HTTPException, Body, Query, Depends, Request
from .manager import I2CManager
from .schemas import I2CControlRequest, I2CStatusResponse
from .exceptions import I2CError, I2CDeviceNotFoundError, I2CInvalidActionError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/i2c", tags=["i2c"])
i2c_manager: I2CManager = None

@router.post("/control", response_model=I2CStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "i2c", "write"))])
async def control_device(req: I2CControlRequest = Body(...)):
    try:
        return await i2c_manager.control(req)
    except I2CDeviceNotFoundError as e:
        logger.warning(f"Device not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except I2CInvalidActionError as e:
        logger.warning(f"Invalid action: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except I2CError as e:
        logger.error(f"I2C error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/status", response_model=I2CStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "i2c", "read"))])
async def get_status(device: str = Query(...)):
    try:
        return await i2c_manager.get_status(device)
    except I2CDeviceNotFoundError as e:
        logger.warning(f"Device not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except I2CError as e:
        logger.error(f"I2C error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/devices", response_model=list[str], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "i2c", "read"))])
async def list_devices():
    return await i2c_manager.list_devices()
