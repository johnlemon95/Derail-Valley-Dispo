from typing import Optional
from pydantic import BaseModel, Field
from common.enums import VehicleType, DriveType


class VehicleBase(BaseModel):
    vehicle_id: str = Field(..., description="e.g. DE2-01", min_length=2)
    vehicle_type: VehicleType
    drive_type: DriveType
    current_station: Optional[str] = None
    current_track: Optional[str] = None
    fuel_percent: float = Field(default=100.0, ge=0.0, le=100.0)
    maintenance_needed: bool = False
    assigned_to_player_id: Optional[int] = None
    assigned_to_username: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int

    model_config = {"from_attributes": True}


class VehicleStatusUpdate(BaseModel):
    current_station: Optional[str] = None
    current_track: Optional[str] = None
    fuel_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    maintenance_needed: Optional[bool] = None
    assigned_to_player_id: Optional[int] = None
    assigned_to_username: Optional[str] = None
