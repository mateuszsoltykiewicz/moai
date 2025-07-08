import aiohttp
import asyncio
import time
from typing import List, Dict, Any, Optional
from .schemas import Alert, Silence, AlertManagerHealth
from .exceptions import AlertManagerConnectionError, AlertManagerAPIError
from .metrics import ALERTMANAGER_OPERATIONS, ALERTMANAGER_LATENCY
from Library.logging import get_logger

logger = get_logger(__name__)

class AlertManagerClient:
    def __init__(self, 
                 base_url: str, 
                 timeout: int = 5,
                 retries: int = 3,
                 retry_delay: float = 0.5,
                 api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.api_key = api_key
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, method: str, endpoint: str, operation_name: str, **kwargs) -> Any:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        start_time = time.monotonic()
        status = "success"
        
        try:
            for attempt in range(self.retries + 1):
                try:
                    async with session.request(method, url, **kwargs) as response:
                        if response.status >= 400:
                            text = await response.text()
                            logger.error(f"AlertManager API error {response.status}: {text}")
                            raise AlertManagerAPIError(f"API error {response.status}: {text}")
                        return await response.json()
                except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
                    if attempt == self.retries:
                        logger.error(f"Connection failed after {self.retries} retries: {e}")
                        raise AlertManagerConnectionError(str(e)) from e
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        except Exception as e:
            status = "error"
            logger.error(f"AlertManager operation failed: {e}", exc_info=True)
            raise
        finally:
            latency = time.monotonic() - start_time
            ALERTMANAGER_LATENCY.labels(operation=operation_name).observe(latency)
            ALERTMANAGER_OPERATIONS.labels(operation=operation_name, status=status).inc()

    async def send_alert(self, alert: Alert) -> Dict[str, Any]:
        """Send a single alert to AlertManager"""
        return await self.send_alerts([alert])

    async def send_alerts(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Send multiple alerts to AlertManager"""
        payload = [alert.dict(exclude_none=True) for alert in alerts]
        return await self._request("POST", "/api/v1/alerts", "send_alerts", json=payload)

    async def get_alerts(
        self, 
        active: bool = True, 
        silenced: bool = True, 
        inhibited: bool = True
    ) -> List[Dict[str, Any]]:
        """Get current alerts from AlertManager"""
        params = {
            "active": str(active).lower(),
            "silenced": str(silenced).lower(),
            "inhibited": str(inhibited).lower()
        }
        return await self._request("GET", "/api/v1/alerts", "get_alerts", params=params)

    async def create_silence(self, silence: Silence) -> Dict[str, Any]:
        """Create a new silence"""
        return await self._request("POST", "/api/v2/silences", "create_silence", json=silence.dict(exclude_none=True))

    async def delete_silence(self, silence_id: str) -> None:
        """Delete a silence by ID"""
        await self._request("DELETE", f"/api/v2/silence/{silence_id}", "delete_silence")

    async def get_silences(self) -> List[Dict[str, Any]]:
        """Get all active silences"""
        return await self._request("GET", "/api/v2/silences", "get_silences")

    async def health_check(self) -> AlertManagerHealth:
        """Check AlertManager health"""
        data = await self._request("GET", "/-/healthy", "health_check")
        return AlertManagerHealth(**data)
