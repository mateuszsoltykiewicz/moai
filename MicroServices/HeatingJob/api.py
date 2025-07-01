from fastapi import APIRouter, Depends, Body, HTTPException, Request
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import HeatingJobManager
from .schemas import HeatingJobTriggerRequest, HeatingJobStatusResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/heating", tags=["heating"])

@router.post("/trigger", response_model=HeatingJobStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "heating", "write"))])
async def trigger_heating_job(request: Request, req: HeatingJobTriggerRequest = Body(...)):
    try:
        status = await HeatingJobManager.trigger_job(req)
        return status
    except Exception as e:
        logger.error(f"Failed to trigger heating job: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.get("/status", response_model=HeatingJobStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "heating", "read"))])
async def get_heating_job_status():
    try:
        status = await HeatingJobManager.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get heating job status: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
