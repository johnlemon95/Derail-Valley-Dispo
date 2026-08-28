from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from backend.database.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    role = Column(String, default="Operator", nullable=False)
    hashed_password = Column(String, nullable=False)
    is_online = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class JobORM(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    job_type = Column(String, nullable=False)
    origin_track = Column(String, nullable=False)
    destination_track = Column(String, nullable=False)
    cargo_description = Column(String, default="")
    wagon_count = Column(Integer, default=0)
    total_weight_tons = Column(Float, default=0.0)
    total_length_m = Column(Float, default=0.0)
    reward = Column(Float, default=0.0)
    is_custom = Column(Boolean, default=False)
    status = Column(String, default="UNCLAIMED", nullable=False)
    claimed_by_player_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    claimed_by_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    claimed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)


class VehicleORM(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, nullable=False, index=True)
    vehicle_type = Column(String, nullable=False)
    drive_type = Column(String, nullable=False)
    current_station = Column(String, nullable=True)
    current_track = Column(String, nullable=True)
    fuel_percent = Column(Float, default=100.0)
    maintenance_needed = Column(Boolean, default=False)
    assigned_to_player_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_username = Column(String, nullable=True)


class TrackORM(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String, unique=True, nullable=False, index=True)
    station_code = Column(String, nullable=False, index=True)
    status = Column(String, default="FREE", nullable=False)
    occupied_by_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)


class StationORM(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
