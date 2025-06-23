# config_client/client.py
import asyncio
from typing import Dict, Any, Callable
from .schemas import ConfigUpdateEvent
import websockets

class ConfigClient:
    def __init__(self, config_server_url: str, service_name: str, env: str):
        self.server_url = config_server_url
        self.service_name = service_name
        self.env = env
        self.config: Dict[str, Any] = {}
        self.listeners = []
        
    async def fetch_initial_config(self):
        """Fetch configuration at startup"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/config/{self.service_name}/{self.env}"
            )
            self.config = response.json()["config"]
    
    async def start_listening(self):
        """Listen for config change events"""
        async with websockets.connect(f"{self.server_url}/ws") as websocket:
            while True:
                event = ConfigUpdateEvent.parse_raw(await websocket.recv())
                if event.service == self.service_name:
                    await self._handle_config_update()
    
    async def _handle_config_update(self):
        """Refresh configuration on change"""
        new_config = await self.fetch_initial_config()
        for listener in self.listeners:
            await listener(self.config, new_config)
        self.config = new_config
    
    def add_change_listener(self, callback: Callable[[dict, dict], None]):
        """Register config change handler"""
        self.listeners.append(callback)
