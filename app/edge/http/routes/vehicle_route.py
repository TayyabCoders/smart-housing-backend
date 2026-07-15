from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class VehicleRegisterRequest(BaseModel):
    plate_number: str
    owner_name: str
    flat_number: Optional[str] = None
    vehicle_type: Optional[str] = "Car"
    color: Optional[str] = None
    status: Optional[str] = "resident"  # resident | visitor | staff | blacklist
    notes: Optional[str] = None


class VehicleStatusRequest(BaseModel):
    status: str  # resident | visitor | staff | blacklist


class VehicleResponse(BaseModel):
    plate_number: str
    owner_name: str
    flat_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[VehicleResponse])
@inject
async def list_vehicles(
    vehicle_repository=Depends(Provide["vehicle_repository"]),
):
    """Return all registered vehicles."""
    vehicles = await vehicle_repository.get_all_vehicles()
    return [
        VehicleResponse(
            plate_number=v.plate_number,
            owner_name=v.owner_name,
            flat_number=v.flat_no,
            vehicle_type=v.vehicle_type,
            color=v.color,
            status=v.status.value if hasattr(v.status, "value") else str(v.status),
        )
        for v in vehicles
    ]


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register_vehicle(
    body: VehicleRegisterRequest,
    vehicle_repository=Depends(Provide["vehicle_repository"]),
):
    """Register a new vehicle or update an existing one."""
    VALID_STATUSES = {"resident", "visitor", "staff", "blacklist"}
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {VALID_STATUSES}")

    vehicle = await vehicle_repository.upsert_vehicle(
        plate_number=body.plate_number.upper().strip(),
        data={
            "owner_name": body.owner_name,
            "flat_no": body.flat_number,
            "vehicle_type": body.vehicle_type or "Car",
            "color": body.color,
            "status": body.status,
            "notes": body.notes,
        },
    )
    return VehicleResponse(
        plate_number=vehicle.plate_number,
        owner_name=vehicle.owner_name,
        flat_number=vehicle.flat_no,
        vehicle_type=vehicle.vehicle_type,
        color=vehicle.color,
        status=vehicle.status.value if hasattr(vehicle.status, "value") else str(vehicle.status),
    )


@router.patch("/{plate_number}/status", response_model=VehicleResponse)
@inject
async def update_vehicle_status(
    plate_number: str,
    body: VehicleStatusRequest,
    vehicle_repository=Depends(Provide["vehicle_repository"]),
):
    """Update the status of a registered vehicle (e.g. mark as blacklist)."""
    VALID_STATUSES = {"resident", "visitor", "staff", "blacklist"}
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {VALID_STATUSES}")

    vehicle = await vehicle_repository.update_status_by_plate(plate_number.upper().strip(), body.status)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return VehicleResponse(
        plate_number=vehicle.plate_number,
        owner_name=vehicle.owner_name,
        flat_number=vehicle.flat_no,
        vehicle_type=vehicle.vehicle_type,
        color=vehicle.color,
        status=vehicle.status.value if hasattr(vehicle.status, "value") else str(vehicle.status),
    )


@router.delete("/{plate_number}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_vehicle(
    plate_number: str,
    vehicle_repository=Depends(Provide["vehicle_repository"]),
):
    """Remove a vehicle from the registry."""
    deleted = await vehicle_repository.delete_by_plate(plate_number.upper().strip())
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle not found")
