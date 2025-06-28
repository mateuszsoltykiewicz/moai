import asyncio
import httpx
import websockets
from typing import Dict, Any, Callable, List, Awaitable
from .schemas import ConfigUpdateEvent
from Library.logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential
from Library.api.security import require_jwt_and_rbac  # For token generation

logger = get_logger(__name__)

class ConfigClient:
    def __init__(self, config_server_url: str, service_name: str, env: str, auth_token: str = None):
        self.server_url = config_server_url
        self.service_name = service_name
        self.env = env
        self.auth_token = auth_token
        self.config: Dict[str, Any] = {}
        self.listeners: List[Callable[[dict, dict], Awaitable[None]]] = []
        self._lock = asyncio.Lock()
        self._ws_task = None
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch_initial_config(self):
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.server_url}/config/{self.service_name}/{self.env}",
                headers=headers
            )
            response.raise_for_status()
            self.config = response.json()["config"]
            logger.info(f"Fetched initial config for {self.service_name}")
    
    async def start_listening(self):
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        while True:
            try:
                async with websockets.connect(
                    f"{self.server_url}/ws",
                    ping_interval=20,
                    ping_timeout=30,
                    extra_headers=headers
                ) as websocket:
                    logger.info("WebSocket connected to config server")
                    while True:
                        message = await websocket.recv()
                        event = ConfigUpdateEvent.parse_raw(message)
                        if event.service == self.service_name:
                            await self._handle_config_update()
            except (websockets.ConnectionClosed, OSError) as e:
                logger.error(f"WebSocket error: {e}. Reconnecting in 5s...", exc_info=True)
                await asyncio.sleep(5)
    
    async def _handle_config_update(self):
        async with self._lock:
            old_config = self.config.copy()
            await self.fetch_initial_config()
            for listener in self.listeners:
                try:
                    await listener(old_config, self.config)
                except Exception as e:
                    logger.error(f"Config listener error: {e}", exc_info=True)
    
    def add_change_listener(self, callback: Callable[[dict, dict], Awaitable[None]]):
        self.listeners.append(callback)
    
    async def stop(self):
        if self._ws_task:
            self._ws_task.cancel()
