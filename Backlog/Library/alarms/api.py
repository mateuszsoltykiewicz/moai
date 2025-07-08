"""
API endpoints for AlarmsManager.

- Exposes /alarms/raise, /alarms/clear, /alarms/{id}, /alarms/
"""

from fastapi import APIRouter, HTTPException, Body, Query
from .manager import AlarmsManager
from .schemas import Alarm, AlarmRaiseRequest, AlarmClearRequest
from .exceptions import AlarmNotFoundError

router = APIRouter(prefix="/alarms", tags=["alarms"])

alarms_manager = AlarmsManager()  # Pass central_registry_url as needed

@router.post("/raise", response_model=Alarm)
async def raise_alarm(req: AlarmRaiseRequest = Body(...)):
    """
    Raise or update an alarm.
    """
    return await alarms_manager.raise_alarm(req)

@router.post("/clear", response_model=Alarm)
async def clear_alarm(req: AlarmClearRequest = Body(...)):
    """
    Clear (deactivate) an alarm.
    """
    try:
        return await alarms_manager.clear_alarm(req)
    except AlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{alarm_id}", response_model=Alarm)
async def get_alarm(alarm_id: str):
    """
    Get alarm by ID.
    """
    try:
        return await alarms_manager.get_alarm(alarm_id)
    except AlarmNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[Alarm])
async def list_alarms(active_only: bool = Query(False)):
    """
    List all alarms, optionally filtering by active status.
    """
    return await alarms_manager.list_alarms(active_only=active_only)
