from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models import Event, Shift, ShiftPriority, ShiftStatus, User
from ..schemas import ShiftCreate, ShiftResponse
from ..services.conflict_detector import detect_conflicts

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _calculate_theoretical_value(base_rate: float, start_time, end_time) -> float:
    duration = end_time - start_time
    hours = max(duration.total_seconds() / 3600, 0)
    return round(hours * base_rate, 2)


def _event_bounds(event: Event, shift_start: datetime, shift_end: datetime) -> tuple[datetime, datetime]:
    tzinfo = shift_start.tzinfo or shift_end.tzinfo
    start_dt = datetime.combine(event.start_date, time.min, tzinfo=tzinfo)
    end_dt = datetime.combine(event.end_date, time.max, tzinfo=tzinfo)
    return start_dt, end_dt


@router.post("/", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == shift_data.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    event_start, event_end = _event_bounds(event, shift_data.start_time, shift_data.end_time)
    if shift_data.start_time < event_start or shift_data.end_time > event_end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Shift dates must be within event dates",
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
        created_by=current_user.id,
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
        event_id=new_shift.event_id,
        status=new_shift.status.value,
        conflicts=new_shift.conflicts or [],
        warnings=warnings,
        economic_value=new_shift.economic_value or {},
        created_at=new_shift.created_at,
        version=new_shift.version,
    )
