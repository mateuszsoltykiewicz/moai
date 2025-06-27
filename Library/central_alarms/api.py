from fastapi import APIRouter, HTTPException, Body, Query, Depends, Security
from fastapi.security import APIKeyHeader
from typing import List
from .manager import CentralAlarmsRegistry
from .schemas import CentralAlarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import CentralAlarmNotFoundError
from .metrics import record_central_alarm_operation

API_KEY_NAME = "X-API-Key"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    # TODO: Replace with Vault or other secure API key validation
    if not api_key or api_key != "YOUR_SECURE_API_KEY":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

router = APIRouter(prefix="/central_alarms", tags=["central_alarms"])

central_alarms_registry: CentralAlarmsRegistry = None  # Inject at app startup

@router.post("/raise", response_model=CentralAlarm, dependencies=[Depends(validate_api_key)])
async def raise_alarm(req: AlarmRaiseRequest = Body(...)):
    try:
        return await central_alarms_registry.raise_alarm(req)
    except Exception as e:
        record_central_alarm_operation("raise", "error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/clear", response_model=CentralAlarm, dependencies=[Depends(validate_api_key)])
async def clear_alarm(req: AlarmClearRequest = Body(...)):
    try:
        return await central_alarms_registry.clear_alarm(req)
    except CentralAlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        record_central_alarm_operation("clear", "error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{alarm_id}", response_model=CentralAlarm, dependencies=[Depends(validate_api_key)])
async def get_alarm(alarm_id: str):
    try:
        return await central_alarms_registry.get_alarm(alarm_id)
    except CentralAlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[CentralAlarm], dependencies=[Depends(validate_api_key)])
async def list_alarms(active_only: bool = Query(False)):
    return await central_alarms_registry.list_alarms(active_only=active_only)
