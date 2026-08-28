import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from common.enums import JobStatus, JobType

TRACK_REGEX = re.compile(r"^[A-Z]{2,3}-[A-Z][0-9]{1,2}[LSOI]?$")


class JobBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=128)
    job_type: JobType
    origin_track: str = Field(..., description="e.g. GF-A1L")
    destination_track: str = Field(..., description="e.g. CS-B2S")
    cargo_description: str = ""
    wagon_count: int = Field(default=0, ge=0)
    total_weight_tons: float = Field(default=0.0, ge=0)
    total_length_m: float = Field(default=0.0, ge=0)
    reward: float = Field(default=0.0, ge=0)
    is_custom: bool = False

    @field_validator("origin_track", "destination_track")
    @classmethod
    def validate_track(cls, v: str) -> str:
        # Custom jobs may use free-text tracks; only validate non-custom via caller
        if not TRACK_REGEX.match(v):
            raise ValueError(f"Ungültiges Gleisformat: '{v}'. Erwartet z.B. GF-A1L")
        return v


class JobCreate(JobBase):
    pass


class JobCreateCustom(BaseModel):
    """Custom jobs bypass track-format validation."""
    title: str = Field(..., min_length=3, max_length=128)
    job_type: JobType = JobType.CUSTOM
    origin_track: str
    destination_track: str
    cargo_description: str = ""
    wagon_count: int = Field(default=0, ge=0)
    total_weight_tons: float = Field(default=0.0, ge=0)
    total_length_m: float = Field(default=0.0, ge=0)
    reward: float = Field(default=0.0, ge=0)
    is_custom: bool = True


class JobResponse(BaseModel):
    id: int
    job_id: str
    title: str
    job_type: JobType
    origin_track: str
    destination_track: str
    cargo_description: str
    wagon_count: int
    total_weight_tons: float
    total_length_m: float
    reward: float
    is_custom: bool
    status: JobStatus
    claimed_by_player_id: Optional[int] = None
    claimed_by_username: Optional[str] = None
    created_at: datetime
    claimed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClaimRequest(BaseModel):
    job_id: int


class ClaimResult(BaseModel):
    success: bool
    message: str
    job: Optional[JobResponse] = None
