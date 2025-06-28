"""
API endpoints for CanbusManager.
"""

from fastapi import APIRouter, HTTPException, Query
from .manager import CanbusManager
from .schemas import CanbusStreamResponse

router = APIRouter(prefix="/canbus", tags=["canbus"])

# Initialize at app startup
canbus_manager: CanbusManager = None

@router.get("/stream", response_model=list[CanbusStreamResponse])
async def stream_sensor(sensor: str = Query(...), limit: int = Query(10, ge=1, le=100)):
    """
    Stream data for a configured sensor.
    """
    try:
        return await canbus_manager.stream_sensor(sensor, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sensors", response_model=list[str])
async def list_sensors():
    """
    List all configured sensor names.
    """
    return await canbus_manager.list_sensors()
