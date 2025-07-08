import asyncio
import websockets
from collections import defaultdict
from .schemas import ConfigUpdateEvent
from Library.logging import get_logger
from Library.api.security import validate_jwt_for_websocket  # New security function

logger = get_logger(__name__)

class ConfigChangeNotifier:
    def __init__(self):
        self.connections = defaultdict(list)
    
    async def notify(self, service_name: str):
        event = ConfigUpdateEvent(service=service_name)
        message = event.json()
        
        for websocket in self.connections.get(service_name, [])[:]:
            try:
                await websocket.send(message)
                logger.debug(f"Notified {service_name} about config change")
            except websockets.ConnectionClosed:
                self.connections[service_name].remove(websocket)
                logger.info(f"Removed closed connection for {service_name}")
    
    async def register(self, service_name: str, websocket, token: str = None):
        """Secure WebSocket registration with JWT validation"""
        if token:
            try:
                # Validate JWT for WebSocket connection
                await validate_jwt_for_websocket(token)
            except Exception as e:
                logger.error(f"WebSocket auth failed: {e}", exc_info=True)
                await websocket.close(code=4001)
                return
        
        self.connections[service_name].append(websocket)
        logger.info(f"New client registered for {service_name}")
