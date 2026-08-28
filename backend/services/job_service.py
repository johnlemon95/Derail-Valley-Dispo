import asyncio
from datetime import datetime, timezone
from config.settings import settings
from backend.database.db_session import SessionLocal
from backend.database.models import JobORM
from common.enums import JobStatus


async def auto_release_disconnected_jobs(
    player_id: int,
    disconnected_at: datetime,
    broadcast_fn,
) -> None:
    """Release claimed jobs if player stays disconnected beyond the timeout."""
    await asyncio.sleep(settings.disconnect_timeout_seconds)
    db = SessionLocal()
    try:
        jobs = (
            db.query(JobORM)
            .filter(
                JobORM.claimed_by_player_id == player_id,
                JobORM.status == JobStatus.CLAIMED,
            )
            .all()
        )
        for job in jobs:
            job.status = JobStatus.UNCLAIMED
            job.claimed_by_player_id = None
            job.claimed_by_username = None
            job.claimed_at = None
        db.commit()
        if jobs:
            await broadcast_fn(
                "job_auto_released",
                {"player_id": player_id, "job_ids": [j.id for j in jobs]},
            )
    finally:
        db.close()
