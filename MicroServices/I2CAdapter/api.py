from fastapi import APIRouter, Depends, Body, HTTPException
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import I2CManager
from .schemas import CommandRequest, CommandResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/i2c", tags=["i2c"])

@router.post("/command", response_model=CommandResponse, dependencies=[Depends(require_jwt_and_rbac)])
async def send_command(request: CommandRequest):
    try:
        result = await I2CManager.execute_command(request.command)
        return CommandResponse(result=result)
    except ValueError as e:
        logger.warning(f"Invalid command: {e}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Command execution failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
