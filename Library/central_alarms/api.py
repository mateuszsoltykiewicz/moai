from fastapi import APIRouter, HTTPException, Body, Query, Depends, Request
from typing import List
from .manager import CentralAlarmsRegistry
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError
from .metrics import record_central_alarm_operation
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/central_alarms", tags=["central_alarms"])

central_alarms_registry: CentralAlarmsRegistry = None  # Inject at app startup

@router.post("/raise", response_model=CentralAlarm, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_alarms", "write"))])
async def raise_alarm(req: AlarmRaiseRequest = Body(...)):
    try:
        return await central_alarms_registry.raise_alarm(req)
    except Exception as e:
        logger.error(f"Error raising alarm: {e}", exc_info=True)
        record_central_alarm_operation("raise", "error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/clear", response_model=CentralAlarm, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_alarms", "write"))])
async def clear_alarm(req: AlarmClearRequest = Body(...)):
    try:
        return await central_alarms_registry.clear_alarm(req)
    except CentralAlarmNotFoundError as e:
        logger.warning(f"Alarm not found: {req.id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing alarm: {e}", exc_info=True)
        record_central_alarm_operation("clear", "error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{alarm_id}", response_model=CentralAlarm, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_alarms", "read"))])
async def get_alarm(alarm_id: str):
    try:
        return await central_alarms_registry.get_alarm(alarm_id)
    except CentralAlarmNotFoundError as e:
        logger.warning(f"Alarm not found: {alarm_id}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[CentralAlarm], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "central_alarms", "read"))])
async def list_alarms(active_only: bool = Query(False)):
    return await central_alarms_registry.list_alarms(active_only=active_only)
