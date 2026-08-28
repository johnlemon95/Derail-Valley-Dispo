import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.database.db_session import SessionLocal
from backend.websockets.connection_manager import manager
from backend.services import claim_service, job_service
from backend.services.auth_service import decode_token
from common.enums import WSEvent

router = APIRouter()


@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int, token: str = ""):
    # Validate token before accepting
    try:
        payload = decode_token(token)
        if payload.get("player_id") != player_id:
            await websocket.close(code=4003)
            return
    except ValueError:
        await websocket.close(code=4001)
        return

    await manager.connect(player_id, websocket)
    await manager.broadcast(WSEvent.PLAYER_CONNECTED, {
        "player_id": player_id,
        "username": payload.get("sub"),
    })

    try:
        while True:
            data = await websocket.receive_json()
            await _handle_event(player_id, payload, data)
    except WebSocketDisconnect:
        manager.disconnect(player_id)
        await manager.broadcast(WSEvent.PLAYER_DISCONNECTED, {"player_id": player_id})
        # Schedule auto-release task
        asyncio.create_task(
            job_service.auto_release_disconnected_jobs(
                player_id,
                datetime.now(timezone.utc),
                manager.broadcast,
            )
        )


async def _handle_event(player_id: int, auth: dict, msg: dict) -> None:
    event = msg.get("event")
    data = msg.get("data", {})
    db = SessionLocal()
    try:
        if event == WSEvent.JOB_CLAIMED:
            result = await claim_service.claim_job(
                job_id=data["job_id"],
                player_id=player_id,
                username=auth["sub"],
                db=db,
            )
            await manager.send_to(player_id, "claim_result", result.model_dump())
            if result.success:
                await manager.broadcast(WSEvent.JOB_CLAIMED, result.job.model_dump())

        elif event == WSEvent.JOB_RELEASED:
            result = await claim_service.release_job(
                job_id=data["job_id"],
                player_id=player_id,
                role=auth["role"],
                db=db,
            )
            await manager.send_to(player_id, "release_result", result.model_dump())
            if result.success:
                await manager.broadcast(WSEvent.JOB_RELEASED, result.job.model_dump())

        elif event == WSEvent.JOB_DELIVERED:
            result = await claim_service.mark_delivered(
                job_id=data["job_id"],
                player_id=player_id,
                role=auth["role"],
                db=db,
            )
            await manager.send_to(player_id, "deliver_result", result.model_dump())
            if result.success:
                await manager.broadcast(WSEvent.JOB_DELIVERED, result.job.model_dump())
    finally:
        db.close()
