import asyncio
import time
from typing import Dict, Any, Optional, List
from .schemas import Session, SessionCreateRequest, SessionUpdateRequest
from .exceptions import SessionNotFoundError
from .metrics import record_session_operation, record_active_sessions
from Library.logging import get_logger
from Library.database.manager import DatabaseManager

logger = get_logger(__name__)

class SessionsManager:
    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager
        self._lock = asyncio.Lock()

    async def create_session(self, req: SessionCreateRequest) -> Session:
        now = time.time()
        expires_at = now + req.expires_in if req.expires_in else None
        session = Session(
            id=req.id,
            data=req.data,
            active=True,
            created_at=now,
            updated_at=now,
            expires_at=expires_at
        )
        async with self._lock:
            await self._db.create_record("sessions", session.dict())
            record_session_operation("create")
            record_active_sessions(await self.count_active_sessions())
            logger.info(f"Created session {session.id}")
            return session

    async def update_session(self, session_id: str, req: SessionUpdateRequest) -> Session:
        async with self._lock:
            session_data = await self._db.get_record("sessions", session_id)
            if not session_data:
                raise SessionNotFoundError(f"Session {session_id} not found")
            session = Session(**session_data)
            now = time.time()
            if req.data:
                session.data.update(req.data)
            if req.active is not None:
                session.active = req.active
            if req.expires_in:
                session.expires_at = now + req.expires_in
            session.updated_at = now
            await self._db.update_record("sessions", session_id, session.dict())
            record_session_operation("update")
            logger.info(f"Updated session {session.id}")
            return session

    async def get_session(self, session_id: str) -> Session:
        async with self._lock:
            session_data = await self._db.get_record("sessions", session_id)
            if not session_data:
                raise SessionNotFoundError(f"Session {session_id} not found")
            session = Session(**session_data)
            if session.expires_at and session.expires_at < time.time():
                await self.delete_session(session_id)
                raise SessionNotFoundError(f"Session {session_id} expired")
            return session

    async def delete_session(self, session_id: str) -> None:
        async with self._lock:
            await self._db.delete_record("sessions", session_id)
            record_session_operation("delete")
            record_active_sessions(await self.count_active_sessions())
            logger.info(f"Deleted session {session_id}")

    async def list_sessions(self, active_only: bool = False, limit: int = 100, offset: int = 0) -> Dict[str, Session]:
        async with self._lock:
            records = await self._db.query_records("sessions", limit=limit, filters={"active": True} if active_only else None)
            now = time.time()
            sessions = {}
            for rec in records:
                session = Session(**rec)
                if session.expires_at and session.expires_at < now:
                    continue
                sessions[session.id] = session
            return sessions

    async def count_active_sessions(self) -> int:
        sessions = await self.list_sessions(active_only=True)
        return len(sessions)
