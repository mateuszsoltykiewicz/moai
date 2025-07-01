from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from Library.logging import get_logger
from .manager import HomeKitBridgeManager

logger = get_logger(__name__)
ws_router = APIRouter()

active_connections = set()

@ws_router.websocket("/ws/accessories")
async def accessories_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Optionally handle incoming messages (e.g., actions from HomeKitProtocolBridge)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_update(update: dict):
    for ws in list(active_connections):
        try:
            await ws.send_json(update)
        except Exception as e:
            logger.warning(f"WebSocket send failed: {e}")
            active_connections.remove(ws)
