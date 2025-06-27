from fastapi import APIRouter, HTTPException, Body, Query, Depends, Security
from fastapi.security import APIKeyHeader
from .manager import SessionsManager
from .schemas import Session, SessionCreateRequest, SessionUpdateRequest
from .exceptions import SessionNotFoundError

API_KEY_NAME = "X-SESSIONS-API-KEY"
api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_scheme)):
    if not api_key or api_key != "SECURE_API_KEY":
        raise HTTPException(403, "Invalid API key")

router = APIRouter(prefix="/sessions", tags=["sessions"])

sessions_manager: SessionsManager = None

@router.post("/", response_model=Session, dependencies=[Depends(validate_api_key)])
async def create_session(req: SessionCreateRequest = Body(...)):
    return await sessions_manager.create_session(req)

@router.put("/{session_id}", response_model=Session, dependencies=[Depends(validate_api_key)])
async def update_session(session_id: str, req: SessionUpdateRequest = Body(...)):
    try:
        return await sessions_manager.update_session(session_id, req)
    except SessionNotFoundError as e:
        raise HTTPException(404, str(e))

@router.get("/{session_id}", response_model=Session, dependencies=[Depends(validate_api_key)])
async def get_session(session_id: str):
    try:
        return await sessions_manager.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(404, str(e))

@router.delete("/{session_id}", status_code=204, dependencies=[Depends(validate_api_key)])
async def delete_session(session_id: str):
    try:
        await sessions_manager.delete_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(404, str(e))

@router.get("/", response_model=Dict[str, Session], dependencies=[Depends(validate_api_key)])
async def list_sessions(
    active_only: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    return await sessions_manager.list_sessions(active_only=active_only, limit=limit, offset=offset)
