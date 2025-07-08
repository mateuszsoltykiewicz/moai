from fastapi import APIRouter, HTTPException, Body, Query, Depends, Request
from typing import List, Optional
from .manager import CentralExceptionsManager
from .schemas import ExceptionPayload
from .exceptions import ExceptionNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/exceptions", tags=["exceptions"])
central_exceptions_manager: CentralExceptionsManager = None  # Inject at app startup

@router.post("/submit", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "exceptions", "write"))])
async def submit_exception(payload: ExceptionPayload = Body(...)):
    try:
        await central_exceptions_manager.process_exception(payload)
        return {"result": "ok"}
    except Exception as e:
        logger.error(f"Failed to process exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/query", response_model=List[ExceptionPayload], dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "exceptions", "read"))])
async def query_exceptions(
    exception_type: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        results = await central_exceptions_manager.query_exceptions(
            exception_type=exception_type,
            service_name=service_name,
            limit=limit
        )
        return results
    except Exception as e:
        logger.error(f"Failed to query exceptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "exceptions", "read"))])
async def get_exception_stats():
    try:
        stats = await central_exceptions_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get exception stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
