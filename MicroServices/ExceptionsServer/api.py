from fastapi import APIRouter, Depends, HTTPException, status
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import ExceptionsManager
from .schemas import ExceptionCreate, ExceptionRead
from typing import List, Optional

logger = get_logger(__name__)
router = APIRouter(prefix="/exceptions", tags=["exceptions"])

@router.post("/", response_model=ExceptionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_jwt_and_rbac)])
async def create_exception(exc: ExceptionCreate):
    try:
        return await ExceptionsManager.create_exception(exc)
    except PermissionError as e:
        logger.warning(f"Unauthorized service exception: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[ExceptionRead], dependencies=[Depends(require_jwt_and_rbac)])
async def list_exceptions(service: Optional[str] = None, status: Optional[str] = None):
    return await ExceptionsManager.list_exceptions(service=service, status=status)

@router.get("/allowed-services", response_model=List[str], dependencies=[Depends(require_jwt_and_rbac)])
async def allowed_services():
    return await ExceptionsManager.get_allowed_services()
