from fastapi import APIRouter, Depends, Request, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import CANBusManager
from .schemas import SensorDataResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/canbus", tags=["canbus"])

@router.get("/sensor-data", response_model=list[SensorDataResponse], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "canbus", "read"))])
async def get_sensor_data():
    try:
        data = await CANBusManager.get_latest_sensor_data()
        return data
    except Exception as e:
        logger.error(f"Failed to get sensor data: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
