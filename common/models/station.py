from typing import List, Optional
from pydantic import BaseModel, Field
from common.enums import TrackStatus


class TrackBase(BaseModel):
    track_id: str = Field(..., description="e.g. GF-A1L")
    station_code: str
    status: TrackStatus = TrackStatus.FREE
    occupied_by_job_id: Optional[int] = None


class TrackResponse(TrackBase):
    id: int

    model_config = {"from_attributes": True}


class TrackStatusUpdate(BaseModel):
    status: TrackStatus
    occupied_by_job_id: Optional[int] = None


class StationBase(BaseModel):
    code: str = Field(..., max_length=5)
    name: str
    description: str = ""


class StationCreate(StationBase):
    pass


class StationResponse(StationBase):
    id: int
    tracks: List[TrackResponse] = []

    model_config = {"from_attributes": True}
