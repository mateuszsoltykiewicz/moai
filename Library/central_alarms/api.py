from fastapi import APIRouter, HTTPException, Body, Query
from .manager import CentralAlarmsRegistry
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError

router = APIRouter(prefix="/central_alarms", tags=["central_alarms"])
central_alarms_registry = CentralAlarmsRegistry()

@router.post("/raise", response_model=CentralAlarm)
async def raise_alarm(req: AlarmRaiseRequest = Body(...)):
    return await central_alarms_registry.raise_alarm(req)

@router.post("/clear", response_model=CentralAlarm)
async def clear_alarm(req: AlarmClearRequest = Body(...)):
    try:
        return await central_alarms_registry.clear_alarm(req)
    except CentralAlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{alarm_id}", response_model=CentralAlarm)
async def get_alarm(alarm_id: str):
    try:
        return await central_alarms_registry.get_alarm(alarm_id)
    except CentralAlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[CentralAlarm])
async def list_alarms(active_only: bool = Query(False)):
    return await central_alarms_registry.list_alarms(active_only=active_only)
