# state/central_state_adapter.py

import httpx
import asyncio
from typing import Dict, Any, Optional
from .exceptions import StateSyncError

class CentralStateRegistryAdapter:
    def __init__(self, csr_url: str):
        self._csr_url = csr_url

    async def push_state(self, service_name: str, state: Dict[str, Any]) -> bool:
        """
        Push local state to the Central State Registry.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._csr_url}/central_state/register",
                    json={
                        "name": service_name,
                        "state": state,
                        "last_heartbeat": datetime.utcnow().isoformat()
                    }
                )
                if response.status_code != 200:
                    raise StateSyncError(f"Failed to push state: {response.text}")
                return True
        except Exception as e:
            raise StateSyncError(f"State sync error: {e}")