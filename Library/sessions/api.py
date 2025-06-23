"""
API endpoints for SessionsManager.

- Exposes /sessions/ for CRUD operations
"""

from fastapi import APIRouter, HTTPException, Body, Query
from .manager import SessionsManager
from .schemas import Session, SessionCreateRequest, SessionUpdateRequest
from .exceptions import SessionNotFoundError

router = APIRouter(prefix="/sessions", tags=["sessions"])

sessions_manager = SessionsManager()

@router.post("/", response_model=Session)
async def create_session(req: SessionCreateRequest = Body(...)):
    """
    Create a new session.
    """
    return await sessions_manager.create_session(req)

@router.put("/{session_id}", response_model=Session)
async def update_session(session_id: str, req: SessionUpdateRequest = Body(...)):
    """
    Update an existing session.
    """
    try:
        return await sessions_manager.update_session(session_id, req)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """
    Retrieve a session by ID.
    """
    try:
        return await sessions_manager.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """
    Delete a session by ID.
    """
    try:
        await sessions_manager.delete_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=Dict[str, Session])
async def list_sessions(active_only: bool = Query(False)):
    """
    List all sessions, optionally filtering by active status.
    """
    return await sessions_manager.list_sessions(active_only=active_only)
