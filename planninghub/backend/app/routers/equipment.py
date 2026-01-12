from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models import Equipment, Shift, User
from ..schemas import (
    EquipmentCreate,
    EquipmentListResponse,
    EquipmentResponse,
    EquipmentStatus,
)

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("/", response_model=EquipmentListResponse)
async def list_equipment(
    category: Optional[str] = Query(default=None),
    status_filter: Optional[EquipmentStatus] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EquipmentListResponse:
    query = db.query(Equipment)
    if category:
        query = query.filter(Equipment.category == category)
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    results = query.all()
    return EquipmentListResponse(
        count=len(results),
        results=results,
    )


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EquipmentResponse:
    roles = current_user.roles or []
    if "admin" not in roles and "manager" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )
    equipment = Equipment(
        **payload.model_dump(mode="json"),
        organization_id=current_user.organization_id,
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.get("/{equipment_id}/availability")
async def equipment_availability(
    equipment_id: UUID,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be after start_time",
        )
    overlapping_shifts = (
        db.query(Shift)
        .filter(Shift.start_time < end_time, Shift.end_time > start_time)
        .all()
    )
    occupied: List[dict] = []
    for shift in overlapping_shifts:
        resources = shift.resources or []
        for resource in resources:
            if resource.get("type") != "equipment":
                continue
            try:
                resource_id = UUID(str(resource.get("id")))
            except (TypeError, ValueError):
                continue
            if resource_id != equipment_id:
                continue
            occupied.append(
                {
                    "shift_id": shift.id,
                    "event_id": shift.event_id,
                    "start_time": shift.start_time,
                    "end_time": shift.end_time,
                }
            )
            break
    return {
        "equipment_id": equipment_id,
        "status": equipment.status,
        "occupied": occupied,
    }
