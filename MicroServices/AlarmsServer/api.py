from fastapi import APIRouter, Depends, Body, Request, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import AlarmsManager
from .schemas import AlarmCreateRequest, AlarmDeleteRequest, AlarmResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/alarms", tags=["alarms"])

@router.post("/create", response_model=AlarmResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "alarms", "write"))])
async def create_alarm(request: Request, req: AlarmCreateRequest = Body(...)):
    try:
        alarm = await AlarmsManager.create_alarm(req)
        return alarm
    except Exception as e:
        logger.error(f"Failed to create alarm: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.post("/delete", response_model=AlarmResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "alarms", "write"))])
async def delete_alarm(request: Request, req: AlarmDeleteRequest = Body(...)):
    try:
        alarm = await AlarmsManager.delete_alarm(req)
        return alarm
    except Exception as e:
        logger.error(f"Failed to delete alarm: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.get("/current", response_model=list[AlarmResponse], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "alarms", "read"))])
async def get_current_alarms():
    try:
        alarms = await AlarmsManager.get_current_alarms()
        return alarms
    except Exception as e:
        logger.error(f"Failed to get current alarms: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
