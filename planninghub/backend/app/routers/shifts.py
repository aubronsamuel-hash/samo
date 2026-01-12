from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shift, ShiftPriority, ShiftStatus
from ..schemas import ShiftCreate, ShiftResponse
from ..services.conflict_detector import detect_conflicts

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _calculate_theoretical_value(base_rate: float, start_time, end_time) -> float:
    duration = end_time - start_time
    hours = max(duration.total_seconds() / 3600, 0)
    return round(hours * base_rate, 2)


@router.post("/", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    x_user_id: UUID | None = Header(default=None, alias="X-User-ID"),
):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing X-User-ID header",
        )

    conflicts, warnings = detect_conflicts(db, shift_data)
    critical_conflicts = [c for c in conflicts if c["severity"] == "critical"]
    if critical_conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RESOURCE_CONFLICT",
                "message": "Conflit critique detecte",
                "conflicts": critical_conflicts,
            },
        )

    economic_value = shift_data.economic_value.model_dump(mode="json")
    economic_value["total_amount"] = _calculate_theoretical_value(
        shift_data.economic_value.base_rate,
        shift_data.start_time,
        shift_data.end_time,
    )

    payload = shift_data.model_dump(mode="json", exclude={"metadata"})
    new_shift = Shift(
        **payload,
        metadata=shift_data.metadata.model_dump(mode="json") if shift_data.metadata else {},
        created_by=x_user_id,
        status=ShiftStatus.CONFIRMED,
        conflicts=conflicts,
        economic_value=economic_value,
        priority=ShiftPriority(shift_data.priority),
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return ShiftResponse(
        id=new_shift.id,
        status=new_shift.status.value,
        conflicts=new_shift.conflicts or [],
        warnings=warnings,
        economic_value=new_shift.economic_value or {},
        created_at=new_shift.created_at,
        version=new_shift.version,
    )
