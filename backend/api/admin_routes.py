from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.db_session import get_db
from backend.database import repository as repo
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    require_admin,
)
from backend.websockets.connection_manager import manager
from common.models.user import UserCreate, UserResponse, TokenResponse
from common.models.job import JobCreate, JobCreateCustom, JobResponse
from common.models.fleet import VehicleCreate, VehicleResponse
from common.models.station import StationCreate, StationResponse
from common.enums import WSEvent

router = APIRouter()


# --- Auth ---

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = repo.get_user_by_username(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    token = create_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        player_id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
    )


# --- User Management (Admin only) ---

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return repo.get_users(db)


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    if repo.get_user_by_username(db, body.username):
        raise HTTPException(status_code=409, detail="Benutzername bereits vergeben")
    return repo.create_user(db, body.username, body.display_name, body.role, hash_password(body.password))


# --- Job Management (Admin only) ---

@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(body: JobCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    job = repo.create_job(db, body)
    resp = JobResponse.model_validate(job)
    await manager.broadcast(WSEvent.JOB_CREATED, resp.model_dump())
    return resp


@router.post("/jobs/custom", response_model=JobResponse, status_code=201)
async def create_custom_job(
    body: JobCreateCustom,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    job = repo.create_job(db, body)
    resp = JobResponse.model_validate(job)
    await manager.broadcast(WSEvent.JOB_CREATED, resp.model_dump())
    return resp


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    if not repo.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    await manager.broadcast(WSEvent.JOB_CANCELLED, {"job_id": job_id})


# --- Fleet Management (Admin only) ---

@router.post("/fleet", response_model=VehicleResponse, status_code=201)
def add_vehicle(body: VehicleCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return repo.create_vehicle(db, body)


@router.delete("/fleet/{vehicle_id}", status_code=204)
def remove_vehicle(vehicle_id: str, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    if not repo.delete_vehicle(db, vehicle_id):
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
