from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db_session import get_db
from backend.database import repository as repo
from backend.services.auth_service import get_current_user
from backend.websockets.connection_manager import manager
from common.models.job import JobCreate, JobResponse, ClaimRequest
from common.enums import WSEvent

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    job_status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return repo.get_jobs(db, status=job_status)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    job = repo.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    return job
