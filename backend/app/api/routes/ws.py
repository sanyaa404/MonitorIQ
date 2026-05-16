# backend/app/api/routes/ws.py
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ws_manager import manager

log = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Keep the connection alive by waiting for messages
        # The browser can send a ping, we just keep looping
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        log.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)