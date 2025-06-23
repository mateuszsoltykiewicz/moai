"""
Session management for StateManager.
"""

from typing import Dict, Any

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Any] = {}

    async def get_session(self, session_id: str) -> Any:
        return self._sessions.get(session_id)

    async def set_session(self, session_id: str,  Any) -> None:
        self._sessions[session_id] = data

    async def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
