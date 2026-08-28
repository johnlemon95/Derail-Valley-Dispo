from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db_session import get_db
from backend.database import repository as repo
from backend.services.auth_service import get_current_user
from backend.websockets.connection_manager import manager
from common.models.fleet import VehicleCreate, VehicleResponse, VehicleStatusUpdate
from common.enums import WSEvent

router = APIRouter()


@router.get("/", response_model=List[VehicleResponse])
def list_vehicles(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return repo.get_vehicles(db)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: str,
    update: VehicleStatusUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    v = repo.update_vehicle_status(db, vehicle_id, update)
    if not v:
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
    await manager.broadcast(WSEvent.VEHICLE_UPDATED, VehicleResponse.model_validate(v).model_dump())
    return v
