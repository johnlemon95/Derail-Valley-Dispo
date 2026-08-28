import json
from datetime import datetime, timezone
from typing import Dict, Optional
from fastapi import WebSocket
from common.enums import WSEvent


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[int, WebSocket] = {}
        self._disconnect_times: Dict[int, datetime] = {}

    async def connect(self, player_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[player_id] = websocket
        self._disconnect_times.pop(player_id, None)

    def disconnect(self, player_id: int) -> None:
        self._connections.pop(player_id, None)
        self._disconnect_times[player_id] = datetime.now(timezone.utc)

    def is_connected(self, player_id: int) -> bool:
        return player_id in self._connections

    def connected_player_ids(self) -> list[int]:
        return list(self._connections.keys())

    async def broadcast(self, event: str, data: dict) -> None:
        payload = json.dumps({"event": event, "data": data})
        dead: list[int] = []
        for pid, ws in list(self._connections.items()):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(pid)
        for pid in dead:
            self.disconnect(pid)

    async def send_to(self, player_id: int, event: str, data: dict) -> None:
        ws = self._connections.get(player_id)
        if ws:
            try:
                await ws.send_text(json.dumps({"event": event, "data": data}))
            except Exception:
                self.disconnect(player_id)


# Singleton used across the application
manager = ConnectionManager()
