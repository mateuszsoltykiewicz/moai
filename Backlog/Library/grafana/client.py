import aiohttp
import asyncio
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .metrics import GRAFANA_OPERATIONS, GRAFANA_LATENCY
from .schemas import DashboardResponse, Annotation, AlertResponse
from Library.logging import get_logger

logger = get_logger(__name__)

def timeit(func):
    async def wrapper(self, *args, **kwargs):
        start_time = time.monotonic()
        operation = func.__name__
        try:
            result = await func(self, *args, **kwargs)
            latency = time.monotonic() - start_time
            GRAFANA_LATENCY.labels(operation=operation).observe(latency)
            GRAFANA_OPERATIONS.labels(operation=operation, status="success").inc()
            return result
        except Exception as e:
            GRAFANA_OPERATIONS.labels(operation=operation, status="error").inc()
            logger.error(f"Grafana client error in {operation}: {e}", exc_info=True)
            raise
    return wrapper

class GrafanaClient:
    def __init__(self, base_url: str, api_token: str, timeout: int = 5, retries: int = 3, retry_delay: float = 0.5):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=headers
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        for attempt in range(self.retries + 1):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        text = await response.text()
                        logger.error(f"Grafana API error {response.status}: {text}")
                        response.raise_for_status()
                    return await response.json()
            except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
                if attempt == self.retries:
                    logger.error(f"Grafana connection failed after {self.retries} retries: {e}", exc_info=True)
                    raise
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            except Exception as e:
                logger.error(f"Unexpected Grafana client error: {e}", exc_info=True)
                raise

    @timeit
    async def get_dashboard(self, uid: str) -> DashboardResponse:
        data = await self._request("GET", f"/api/dashboards/uid/{uid}")
        return DashboardResponse(**data)

    @timeit
    async def push_annotation(self, annotation: Annotation) -> Dict[str, Any]:
        payload = annotation.dict(exclude_none=True)
        return await self._request("POST", "/api/annotations", json=payload)

    @timeit
    async def query_alerts(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/alerts")

    @timeit
    async def health_check(self) -> bool:
        try:
            data = await self._request("GET", "/api/health")
            return data.get("database", "ok") == "ok"
        except Exception:
            return False
