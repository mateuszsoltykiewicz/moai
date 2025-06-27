import httpx
import asyncio
from datetime import datetime
from .exceptions import StateSyncError
from tenacity import retry, stop_after_attempt, wait_exponential

class CentralStateRegistryAdapter:
    def __init__(self, csr_url: str):
        self._csr_url = csr_url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def push_state(self, service_name: str, state: Dict[str, Any]) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self._csr_url}/central_state/register",
                    json={
                        "name": service_name,
                        "state": state,
                        "last_heartbeat": datetime.utcnow().isoformat()
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            raise StateSyncError(f"State sync failed: {str(e)}")
