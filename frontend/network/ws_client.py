import asyncio
import json
import websockets
from typing import Callable, Optional
from frontend.state.app_state import AppState
from common.enums import WSEvent


class WSClient:
    def __init__(self, base_ws_url: str, state: AppState):
        self._base = base_ws_url.rstrip("/")
        self._state = state
        self._ws = None
        self._running = False
        self._on_event: Optional[Callable] = None  # ui refresh callback

    def set_event_callback(self, fn: Callable) -> None:
        self._on_event = fn

    async def connect(self) -> None:
        url = f"{self._base}/ws/{self._state.player_id}?token={self._state.token}"
        self._running = True
        try:
            async with websockets.connect(url) as ws:
                self._ws = ws
                async for raw in ws:
                    msg = json.loads(raw)
                    self._dispatch(msg.get("event"), msg.get("data", {}))
        except Exception:
            self._running = False
            self._ws = None

    def _dispatch(self, event: str, data: dict) -> None:
        match event:
            case WSEvent.JOB_CLAIMED | WSEvent.JOB_RELEASED | WSEvent.JOB_IN_TRANSIT | WSEvent.JOB_DELIVERED:
                if job := data:
                    self._state.upsert_job(job)
            case WSEvent.JOB_CREATED:
                self._state.upsert_job(data)
            case WSEvent.JOB_CANCELLED:
                self._state.remove_job(data.get("job_id"))
            case "job_auto_released":
                for jid in data.get("job_ids", []):
                    for j in self._state.jobs:
                        if j["id"] == jid:
                            j["status"] = "UNCLAIMED"
                            j["claimed_by_username"] = None
            case WSEvent.VEHICLE_UPDATED:
                self._state.upsert_vehicle(data)
            case WSEvent.PLAYER_CONNECTED:
                pid = data.get("player_id")
                if not any(p["player_id"] == pid for p in self._state.connected_players):
                    self._state.connected_players.append(data)
            case WSEvent.PLAYER_DISCONNECTED:
                pid = data.get("player_id")
                self._state.connected_players = [
                    p for p in self._state.connected_players if p["player_id"] != pid
                ]
        if self._on_event:
            self._on_event(event, data)

    async def send(self, event: str, data: dict) -> None:
        if self._ws:
            await self._ws.send(json.dumps({"event": event, "data": data}))

    async def claim_job(self, job_id: int) -> None:
        await self.send(WSEvent.JOB_CLAIMED, {"job_id": job_id})

    async def release_job(self, job_id: int) -> None:
        await self.send(WSEvent.JOB_RELEASED, {"job_id": job_id})

    async def deliver_job(self, job_id: int) -> None:
        await self.send(WSEvent.JOB_DELIVERED, {"job_id": job_id})

    def disconnect(self) -> None:
        self._running = False
        if self._ws:
            asyncio.create_task(self._ws.close())
