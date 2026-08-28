from typing import Optional
from sqlalchemy.orm import Session
from backend.database.models import JobORM, UserORM, VehicleORM, TrackORM, StationORM
from common.models.job import JobCreate, JobCreateCustom
from common.models.fleet import VehicleCreate, VehicleStatusUpdate
from common.models.station import TrackStatusUpdate, StationCreate
from common.enums import JobStatus


# --- Jobs ---

def get_jobs(db: Session, status: Optional[str] = None) -> list[JobORM]:
    q = db.query(JobORM)
    if status:
        q = q.filter(JobORM.status == status)
    return q.order_by(JobORM.created_at.desc()).all()


def get_job_by_id(db: Session, job_id: int) -> Optional[JobORM]:
    return db.query(JobORM).filter(JobORM.id == job_id).first()


def create_job(db: Session, job_data: JobCreate | JobCreateCustom) -> JobORM:
    count = db.query(JobORM).count() + 1
    job_id = f"{job_data.origin_track[:min(3, len(job_data.origin_track))]}-{job_data.job_type}-{count:03d}"
    orm = JobORM(**job_data.model_dump(), job_id=job_id)
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return orm


def delete_job(db: Session, job_id: int) -> bool:
    job = db.query(JobORM).filter(JobORM.id == job_id).first()
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True


# --- Vehicles ---

def get_vehicles(db: Session) -> list[VehicleORM]:
    return db.query(VehicleORM).all()


def get_vehicle(db: Session, vehicle_id: str) -> Optional[VehicleORM]:
    return db.query(VehicleORM).filter(VehicleORM.vehicle_id == vehicle_id).first()


def create_vehicle(db: Session, data: VehicleCreate) -> VehicleORM:
    orm = VehicleORM(**data.model_dump())
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return orm


def update_vehicle_status(db: Session, vehicle_id: str, update: VehicleStatusUpdate) -> Optional[VehicleORM]:
    v = db.query(VehicleORM).filter(VehicleORM.vehicle_id == vehicle_id).first()
    if not v:
        return None
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(v, field, value)
    db.commit()
    db.refresh(v)
    return v


def delete_vehicle(db: Session, vehicle_id: str) -> bool:
    v = db.query(VehicleORM).filter(VehicleORM.vehicle_id == vehicle_id).first()
    if not v:
        return False
    db.delete(v)
    db.commit()
    return True


# --- Tracks & Stations ---

def get_tracks(db: Session, station_code: Optional[str] = None) -> list[TrackORM]:
    q = db.query(TrackORM)
    if station_code:
        q = q.filter(TrackORM.station_code == station_code)
    return q.all()


def update_track_status(db: Session, track_id: str, update: TrackStatusUpdate) -> Optional[TrackORM]:
    t = db.query(TrackORM).filter(TrackORM.track_id == track_id).first()
    if not t:
        return None
    t.status = update.status
    t.occupied_by_job_id = update.occupied_by_job_id
    db.commit()
    db.refresh(t)
    return t


def get_stations(db: Session) -> list[StationORM]:
    return db.query(StationORM).all()


# --- Users ---

def get_user_by_username(db: Session, username: str) -> Optional[UserORM]:
    return db.query(UserORM).filter(UserORM.username == username).first()


def get_users(db: Session) -> list[UserORM]:
    return db.query(UserORM).all()


def create_user(db: Session, username: str, display_name: str, role: str, hashed_password: str) -> UserORM:
    u = UserORM(username=username, display_name=display_name, role=role, hashed_password=hashed_password)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def set_user_online(db: Session, user_id: int, online: bool) -> None:
    u = db.query(UserORM).filter(UserORM.id == user_id).first()
    if u:
        u.is_online = online
        db.commit()
