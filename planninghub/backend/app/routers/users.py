import re
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models import Shift, User
from ..schemas import (
    AvailabilityPayload,
    AvailabilityUpdateResponse,
    AvailabilityWarning,
    UserProfile,
)

router = APIRouter(prefix="/users", tags=["users"])

TIME_RANGE_PATTERN = re.compile(
    r"^([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]$"
)


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me/availability", response_model=AvailabilityUpdateResponse)
async def update_availability(
    availability_payload: AvailabilityPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AvailabilityUpdateResponse:
    updates = _normalize_availability_payload(availability_payload.root)
    current_availability = dict(current_user.availability or {})
    for day, ranges in updates.items():
        current_availability[day] = ranges
    current_user.availability = current_availability
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    warnings = _availability_warnings(db, current_user, updates)
    return AvailabilityUpdateResponse(
        status="success",
        availability=current_user.availability or {},
        warnings=warnings,
    )


def _normalize_availability_payload(
    payload: Dict[str, Optional[List[str]]]
) -> Dict[str, List[str]]:
    normalized: Dict[str, List[str]] = {}
    for day, ranges in payload.items():
        if ranges is None:
            normalized[day] = []
            continue
        normalized[day] = ranges
    return normalized


def _availability_warnings(
    db: Session, current_user: User, updates: Dict[str, List[str]]
) -> List[AvailabilityWarning]:
    warnings: List[AvailabilityWarning] = []
    for day, ranges in updates.items():
        day_date = _parse_date(day)
        day_start = datetime.combine(day_date, time.min)
        day_end = datetime.combine(day_date + timedelta(days=1), time.min)
        shifts = (
            db.query(Shift)
            .filter(
                Shift.assignee_id == current_user.id,
                Shift.start_time < day_end,
                Shift.end_time > day_start,
            )
            .all()
        )
        if not shifts:
            continue
        range_windows = _range_windows(day_date, ranges)
        for shift in shifts:
            if not _shift_fits_ranges(shift.start_time, shift.end_time, range_windows):
                warnings.append(
                    AvailabilityWarning(
                        date=day,
                        message=(
                            "Ce creneau chevauche un shift existant "
                            f"({shift.id}). Le conflit sera resolu par le regisseur."
                        ),
                        severity="medium",
                    )
                )
    return warnings


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format for availability: {value}",
        ) from exc


def _range_windows(day_date: date, ranges: List[str]) -> List[Tuple[datetime, datetime]]:
    windows: List[Tuple[datetime, datetime]] = []
    for time_range in ranges:
        if not TIME_RANGE_PATTERN.match(time_range):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid time range format: {time_range}",
            )
        start_str, end_str = time_range.split("-", 1)
        start_time = _parse_time(start_str)
        end_time = _parse_time(end_str)
        start_dt = datetime.combine(day_date, start_time)
        end_dt = datetime.combine(day_date, end_time)
        if end_dt <= start_dt:
            end_dt = datetime.combine(day_date + timedelta(days=1), end_time)
        windows.append((start_dt, end_dt))
    return windows


def _parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _shift_fits_ranges(
    shift_start: datetime,
    shift_end: datetime,
    ranges: List[Tuple[datetime, datetime]],
) -> bool:
    if not ranges:
        return False
    for range_start, range_end in ranges:
        if shift_start >= range_start and shift_end <= range_end:
            return True
    return False
