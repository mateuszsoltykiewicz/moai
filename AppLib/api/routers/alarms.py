"""
Alarms API Router

- Allows creation, listing, and querying of system alarms.
- All endpoints are async and use Pydantic schemas.
- Authenticated access is required for all operations.
- Ready for integration with an alarms subservice or DB backend.
"""

from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from models.alarms import Alarm, AlarmLevel
from api.dependencies import get_current_user
from api.main import APIException

router = APIRouter(tags=["alarms"])

# Example: In-memory alarm store (replace with DB/service integration in production)
ALARMS: List[Alarm] = []

@router.get(
    "/",
    response_model=List[Alarm],
    summary="List all alarms",
    description="Retrieve all alarms, optionally filtered by level."
)
async def list_alarms(
    level: Optional[AlarmLevel] = Query(None, description="Filter by alarm level"),
    user=Depends(get_current_user)
):
    """
    List all alarms, optionally filtering by severity level.
    """
    if level:
        return [alarm for alarm in ALARMS if alarm.level == level]
    return ALARMS

@router.post(
    "/",
    response_model=Alarm,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alarm"
)
async def create_alarm(
    alarm: Alarm,
    user=Depends(get_current_user)
):
    """
    Create a new alarm event.
    """
    # In production, insert into DB or send to alarms subservice
    ALARMS.append(alarm)
    return alarm

@router.get(
    "/{code}",
    response_model=Alarm,
    summary="Get alarm by code"
)
async def get_alarm_by_code(
    code: str,
    user=Depends(get_current_user)
):
    """
    Retrieve a single alarm by its unique code.
    """
    for alarm in ALARMS:
        if alarm.code == code:
            return alarm
    raise APIException(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Alarm not found",
        details={"code": code}
    )
