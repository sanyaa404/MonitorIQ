# backend/app/services/ws_manager.py
import logging
import json
from typing import Set
from fastapi import WebSocket

log = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Set of all currently connected WebSocket clients
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        log.info(f"Client connected | total={len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        log.info(f"Client disconnected | total={len(self.active_connections)}")

    async def broadcast(self, data: dict):
        if not self.active_connections:
            return

        message = json.dumps(data, default=str)
        disconnected = set()

        for websocket in self.active_connections.copy():
            try:
                await websocket.send_text(message)
            except Exception:
                # Client disconnected ungracefully
                disconnected.add(websocket)

        # Clean up dead connections
        for websocket in disconnected:
            self.disconnect(websocket)


# Single shared instance used across the entire app
manager = ConnectionManager()