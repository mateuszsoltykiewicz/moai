from fastapi import APIRouter, HTTPException, Body, Query, Depends, Request
from .manager import SessionsManager
from .schemas import Session, SessionCreateRequest, SessionUpdateRequest
from .exceptions import SessionNotFoundError
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])
sessions_manager: SessionsManager = None

@router.post("/", response_model=Session, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "sessions", "create"))])
async def create_session(req: SessionCreateRequest = Body(...)):
    return await sessions_manager.create_session(req)

@router.put("/{session_id}", response_model=Session, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "sessions", "update"))])
async def update_session(session_id: str, req: SessionUpdateRequest = Body(...)):
    try:
        return await sessions_manager.update_session(session_id, req)
    except SessionNotFoundError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(404, str(e))

@router.get("/{session_id}", response_model=Session, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "sessions", "read"))])
async def get_session(session_id: str):
    try:
        return await sessions_manager.get_session(session_id)
    except SessionNotFoundError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(404, str(e))

@router.delete("/{session_id}", status_code=204, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "sessions", "delete"))])
async def delete_session(session_id: str):
    try:
        await sessions_manager.delete_session(session_id)
    except SessionNotFoundError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(404, str(e))

@router.get("/", response_model=dict, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "sessions", "read"))])
async def list_sessions(
    active_only: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    return await sessions_manager.list_sessions(active_only=active_only, limit=limit, offset=offset)
