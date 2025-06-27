import asyncio
import websockets
from collections import defaultdict
from .schemas import ConfigUpdateEvent
from .utils import log_error
from Library.mtls.manager import MtlsManager

class ConfigChangeNotifier:
    def __init__(self, mtls_manager: MtlsManager = None):
        self.connections = defaultdict(list)
        self.mtls_manager = mtls_manager
    
    async def notify(self, service_name: str):
        """Efficient broadcasting with connection management"""
        event = ConfigUpdateEvent(service=service_name)
        message = event.json()
        
        for websocket in self.connections.get(service_name, [])[:]:  # Copy list
            try:
                await websocket.send(message)
            except websockets.ConnectionClosed:
                self.connections[service_name].remove(websocket)
    
    async def register(self, service_name: str, websocket):
        """Secure registration with MTLS verification"""
        if self.mtls_manager:
            # Verify client certificate
            if not await self.mtls_manager.verify_connection(websocket):
                log_error(f"Rejected unverified connection for {service_name}")
                await websocket.close(code=4001)
                return
        
        self.connections[service_name].append(websocket)
        log_info(f"New client registered for {service_name}")
