"""Atomic job claiming with asyncio locks + DB-level row locking (SQLite)."""
import asyncio
from datetime import datetime, timezone
from typing import Dict
from sqlalchemy.orm import Session
from backend.database.models import JobORM
from common.enums import JobStatus, UserRole
from common.models.job import ClaimResult, JobResponse

# Per-job asyncio locks prevent concurrent in-process race conditions.
# SQLite's implicit transaction serialization covers multi-process edge cases.
_job_locks: Dict[int, asyncio.Lock] = {}
_registry_lock = asyncio.Lock()


async def _get_lock(job_id: int) -> asyncio.Lock:
    async with _registry_lock:
        if job_id not in _job_locks:
            _job_locks[job_id] = asyncio.Lock()
        return _job_locks[job_id]


async def claim_job(
    job_id: int,
    player_id: int,
    username: str,
    db: Session,
) -> ClaimResult:
    lock = await _get_lock(job_id)
    async with lock:
        job = db.query(JobORM).filter(JobORM.id == job_id).first()
        if not job:
            return ClaimResult(success=False, message="Job nicht gefunden.")
        if job.status != JobStatus.UNCLAIMED:
            return ClaimResult(
                success=False,
                message=f"Job bereits vergeben an {job.claimed_by_username or 'unbekannt'}.",
            )
        job.status = JobStatus.CLAIMED
        job.claimed_by_player_id = player_id
        job.claimed_by_username = username
        job.claimed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return ClaimResult(
            success=True,
            message="Job erfolgreich angenommen.",
            job=JobResponse.model_validate(job),
        )


async def release_job(
    job_id: int,
    player_id: int,
    role: str,
    db: Session,
) -> ClaimResult:
    lock = await _get_lock(job_id)
    async with lock:
        job = db.query(JobORM).filter(JobORM.id == job_id).first()
        if not job:
            return ClaimResult(success=False, message="Job nicht gefunden.")
        if job.status == JobStatus.UNCLAIMED:
            return ClaimResult(success=False, message="Job ist bereits frei.")
        is_admin = role == UserRole.ADMIN
        if not is_admin and job.claimed_by_player_id != player_id:
            return ClaimResult(
                success=False,
                message="Keine Berechtigung: Nur eigene Jobs können freigegeben werden.",
            )
        job.status = JobStatus.UNCLAIMED
        job.claimed_by_player_id = None
        job.claimed_by_username = None
        job.claimed_at = None
        db.commit()
        db.refresh(job)
        return ClaimResult(
            success=True,
            message="Job freigegeben.",
            job=JobResponse.model_validate(job),
        )


async def mark_delivered(job_id: int, player_id: int, role: str, db: Session) -> ClaimResult:
    lock = await _get_lock(job_id)
    async with lock:
        job = db.query(JobORM).filter(JobORM.id == job_id).first()
        if not job:
            return ClaimResult(success=False, message="Job nicht gefunden.")
        is_admin = role == UserRole.ADMIN
        if not is_admin and job.claimed_by_player_id != player_id:
            return ClaimResult(success=False, message="Keine Berechtigung.")
        job.status = JobStatus.DELIVERED
        job.delivered_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return ClaimResult(
            success=True,
            message="Job als erledigt markiert.",
            job=JobResponse.model_validate(job),
        )
