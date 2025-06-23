"""
SessionsManager: Centralized async session management.

- Manages sessions for adapters, hardware, and other resources
- Supports session creation, retrieval, update, and deletion
- Integrates with metrics, logging, and all components
- Async and thread-safe
"""

import asyncio
from typing import Dict, Any, Optional
from .schemas import Session, SessionCreateRequest, SessionUpdateRequest
from .exceptions import SessionNotFoundError
from .metrics import record_session_operation
from .utils import log_info

class SessionsManager:
    """
    Central manager for sessions in the application.
    Provides async methods for creating, updating, retrieving, and deleting sessions.
    """
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, req: SessionCreateRequest) -> Session:
        """
        Create a new session.

        Args:
            req: SessionCreateRequest with id and data

        Returns:
            Session: The created Session object
        """
        async with self._lock:
            session = Session(
                id=req.id,
                data=req.data,
                active=True
            )
            self._sessions[session.id] = session
            record_session_operation("create")
            log_info(f"SessionsManager: Created session {session.id}")
            return session

    async def update_session(self, session_id: str, req: SessionUpdateRequest) -> Session:
        """
        Update an existing session.

        Args:
            session_id: The session ID to update
            req: SessionUpdateRequest with updated data

        Returns:
            Session: The updated Session object

        Raises:
            SessionNotFoundError: If session with given id does not exist
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(f"Session {session_id} not found")
            if req.data is not None:
                session.data.update(req.data)
            if req.active is not None:
                session.active = req.active
            record_session_operation("update")
            log_info(f"SessionsManager: Updated session {session.id}")
            return session

    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve a session by ID.

        Args:
            session_id: The session ID

        Returns:
            Session: The Session object

        Raises:
            SessionNotFoundError: If session with given id does not exist
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(f"Session {session_id} not found")
            return session

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session by ID.

        Args:
            session_id: The session ID

        Raises:
            SessionNotFoundError: If session with given id does not exist
        """
        async with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFoundError(f"Session {session_id} not found")
            del self._sessions[session_id]
            record_session_operation("delete")
            log_info(f"SessionsManager: Deleted session {session_id}")

    async def list_sessions(self, active_only: bool = False) -> Dict[str, Session]:
        """
        List all sessions, optionally filtering by active status.

        Args:
            active_only: If True, only return active sessions

        Returns:
            Dict[str, Session]: Dictionary of session_id to Session objects
        """
        async with self._lock:
            if active_only:
                return {sid: s for sid, s in self._sessions.items() if s.active}
            return dict(self._sessions)
