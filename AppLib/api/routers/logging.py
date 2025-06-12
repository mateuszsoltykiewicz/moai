from fastapi import APIRouter, Depends, status
from models.schemas import (
    LogLevelUpdateRequest, LogLevelUpdateResponse,
    LoggerStatus, LoggerListResponse
)
from api.dependencies import get_current_user
from api.main import APIException
import logging

router = APIRouter(tags=["logging"])

@router.get(
    "/",
    response_model=LoggerListResponse,
    summary="List all loggers and their levels"
)
async def list_loggers(user=Depends(get_current_user)):
    loggers = []
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        loggers.append(LoggerStatus(
            logger_name=name,
            level=logging.getLevelName(logger.level)
        ))
    root_logger = logging.getLogger()
    loggers.append(LoggerStatus(
        logger_name="",
        level=logging.getLevelName(root_logger.level)
    ))
    return LoggerListResponse(loggers=loggers)

@router.post(
    "/level",
    response_model=LogLevelUpdateResponse,
    summary="Update log level for a logger"
)
async def update_log_level(
    req: LogLevelUpdateRequest,
    user=Depends(get_current_user)
):
    try:
        logger = logging.getLogger(req.logger_name)
        old_level = logging.getLevelName(logger.level)
        logger.setLevel(req.level.upper())
        new_level = logging.getLevelName(logger.level)
        return LogLevelUpdateResponse(
            logger_name=req.logger_name,
            old_level=old_level,
            new_level=new_level
        )
    except Exception as e:
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to update log level.",
            details={"error": str(e)}
        )
