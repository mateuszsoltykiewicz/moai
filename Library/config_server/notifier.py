# config_server/notifier.py
import asyncio
import websockets
from collections import defaultdict
from schemas import ConfigResponse, ConfigUpdateEvent

class ConfigChangeNotifier:
    def __init__(self):
        self.connections = defaultdict(list)
    
    async def notify(self, service_name: str):
        """Notify all connected clients of config changes"""
        for websocket in self.connections.get(service_name, []):
            try:
                await websocket.send(ConfigUpdateEvent(service=service_name).json())
            except websockets.ConnectionClosed:
                self.connections[service_name].remove(websocket)
    
    async def register(self, service_name: str, websocket):
        """Register new client connection"""
        self.connections[service_name].append(websocket)
